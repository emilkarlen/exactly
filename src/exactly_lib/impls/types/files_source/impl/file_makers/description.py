from typing import Sequence, Optional, Mapping

from exactly_lib.impls.types.files_source.defs import FileType, ModificationType
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.description_tree.tree import Detail
from ... import syntax


def _formatted_file_type_tokens() -> Mapping[FileType, str]:
    max_token_len = max(map(len, syntax.FILE_TYPE_TOKENS.values()))
    return {
        ft: tok + ((max_token_len - len(tok)) * ' ')
        for ft, tok in syntax.FILE_TYPE_TOKENS.items()
    }


_FORMATTED_FILE_TYPE_TOKENS = _formatted_file_type_tokens()


class Describer(DetailsRenderer):
    def __init__(self,
                 file_type: FileType,
                 modification_type: ModificationType,
                 file_name: str,
                 contents_description: Optional[DetailsRenderer],
                 ):
        self._file_type = file_type
        self._modification_type = modification_type
        self._file_name = file_name
        self._contents_description = contents_description

    def render(self) -> Sequence[Detail]:
        return self._renderer().render()

    def _renderer(self) -> DetailsRenderer:
        header_parts = [_FORMATTED_FILE_TYPE_TOKENS[self._file_type],
                        self._file_name]
        if self._contents_description is not None:
            header_parts.append(syntax.MODIFICATION_VARIANT_TOKENS[self._modification_type])

        header = ' '.join(header_parts)
        return (
            details.String(header)
            if self._contents_description is None
            else
            details.HeaderAndValue(header, self._contents_description)
        )
