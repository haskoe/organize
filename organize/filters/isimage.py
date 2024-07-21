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
class IsImage:
    filter_config: ClassVar[FilterConfig] = FilterConfig(
        name="isimage",
        files=True,
        dirs=False,
    )

    def pipeline(self, res: Resource, output: Output) -> bool:
        result = res.vars['mimetype'].split('/')[0] == 'image'
        result = result and res.vars['mimetypemagic'].split('/')[0] == 'image'
        if result:
            res.vars[self.filter_config.name] = result
        return result
