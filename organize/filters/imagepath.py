from os import path
import hashlib
from pathlib import Path
from typing import ClassVar

from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource
from organize.template import Template, render


def hash(path: Path, algo: str, *, _bufsize=2**18) -> str:
    # for python >= 3.11 we can use hashlib.file_digest
    if hasattr(hashlib, "file_digest"):
        with path.open("rb") as f:
            return hashlib.file_digest(f, algo, _bufsize=_bufsize).hexdigest()

    # otherwise we have to use our own backported implementation:
    h = hashlib.new(algo)
    buf = bytearray(_bufsize)
    view = memoryview(buf)
    with path.open("rb", buffering=0) as f:
        while size := f.readinto(buf):
            h.update(view[:size])
    return h.hexdigest()


def hash_first_chunk(path: Path, algo: str, *, chunksize=1024) -> str:
    h = hashlib.new(algo)
    with path.open("rb") as f:
        chunk = f.read(chunksize)
        h.update(chunk)
    return h.hexdigest()


@dataclass(config=ConfigDict(extra="forbid"))
class ImagePath:
    """
    - `{imagepath}`:  The hash of the file.
    """

    filter_config: ClassVar[FilterConfig] = FilterConfig(
        name="imagepath",
        files=True,
        dirs=False,
    )

    def pipeline(self, res: Resource, output: Output) -> bool:
        assert res.path is not None

        result = ''
        bodyserialnumber = ''
        if res.vars['isimage']:
            exif = res.vars.get('exif',{})
            exif_exif = exif.get('exif',{})
            exif_image = exif.get('image',{})
            model = exif_image.get('model','').replace(' ','')
            if model:
                bodyserialnumber = exif_exif.get('bodyserialnumber')
                if bodyserialnumber:
                    print(bodyserialnumber)
                    model = '%s-%s' % (model,bodyserialnumber)
            else:
                model = '' #len(exif) == 0 and 'noexif' or 'nomodel'

            fname = '%s_%s.%s' % (res.vars['hashraw'][:20], res.vars['size']['bytes'], res.vars['mimeextension'])
            datetimeoriginal = exif_exif.get('datetimeoriginal')
            if datetimeoriginal:
                fname = path.join(datetimeoriginal.strftime('%Y'),datetimeoriginal.strftime('%m'), '%s_%s' % (datetimeoriginal.strftime('%Y%m%d_%H%M%S'),fname))
            
            if model:
                fname = path.join(model,fname)
            result = path.join( res.vars['mimeextension'], fname).lower()
            res.vars[self.filter_config.name] = result
        return result
