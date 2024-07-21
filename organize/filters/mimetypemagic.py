import magic
from typing import ClassVar

from pydantic import Field
from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource
from organize.validators import FlatList


def guess_mimetype(path):
    mime = magic.Magic(mime=True)
    return mime.from_file(path)


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
class MimeTypeMagic:
    """Filter by magic MIME type associated with the file extension.

    Supports a single string or list of MIME type strings as argument.
    The types don't need to be fully specified, for example "audio" matches everything
    from "audio/midi" to "audio/quicktime".

    You can see a list of known MIME types on your system by running this oneliner:

    ```sh
    python3 -m organize.filters.mimetype
    ```

    Attributes:
        *mimetypes (list(str) or str): The MIME types to filter for.

    **Returns:**

    - `{mimetypemagic}`: The MIME type of the file.
    """

    mimetypes: FlatList[str] = Field(default_factory=list)

    filter_config: ClassVar[FilterConfig] = FilterConfig(
        name="mimetypemagic",
        files=True,
        dirs=False,
    )

    def matches(self, mimetype) -> bool:
        if mimetype is None:
            return False
        if not self.mimetypes:
            return True
        return any(mimetype.startswith(x) for x in self.mimetypes)

    def pipeline(self, res: Resource, output: Output) -> bool:
        mimetype = guess_mimetype(res.path)
        #exif_mimetype = res.vars.get('exif',{}).get('file',{}).get('mimetype')
        #if exif_mimetype:
        #    mimetype = exif_mimetype
        #else:
        #    mimetype = guess_mimetype(res.path)
        res.vars[self.filter_config.name] = mimetype
        return self.matches(mimetype)
