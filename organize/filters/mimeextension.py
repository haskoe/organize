import mimetypes
from typing import ClassVar, Set, Tuple

from pydantic import Field, field_validator
from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource
from organize.validators import flatten


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
class MimeExtension:
    """Filter by mime type preferred extension

    Attributes:
        *extensions (list(str) or str):
            The file extensions to match (does not need to start with a colon).

    **Returns:**

    - `{mimeextension}`: the original file extension (without colon)
    """

    extensions: Set[str] = Field(default_factory=set)

    filter_config: ClassVar[FilterConfig] = FilterConfig(
        name="mimeextension",
        files=True,
        dirs=False,
    )

    def pipeline(self, res: Resource, output: Output) -> bool:
        assert res.path is not None, "Does not support standalone mode"
        if res.is_dir():
            raise ValueError("Dirs not supported")

        ext = mimetypes.guess_extension(res.vars['mimetypemagic'])
        ext = ext and ext.startswith('.') and ext[1:] or ext
        res.vars[self.filter_config.name] = ext or ''
        return ext
