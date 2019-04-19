from pathlib import Path
from typing import Sequence, Optional

from exactly_lib.section_document.exceptions import FileAccessError
from exactly_lib.section_document.impl.utils import new_for_file
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import SourceLocation


def read_source_file(file_path: Path,
                     file_path_for_error_message: Path,
                     file_inclusion_chain: Sequence[SourceLocation],
                     section_name: Optional[str] = None,
                     ) -> ParseSource:
    try:
        return new_for_file(file_path)
    except OSError as ex:
        raise FileAccessError(file_path_for_error_message,
                              str(ex),
                              file_inclusion_chain,
                              section_name)


def resolve_path(path: Path,
                 file_inclusion_chain: Sequence[SourceLocation],
                 section_name: Optional[str] = None,
                 ) -> Path:
    try:
        return path.resolve()
    except RuntimeError as ex:
        raise FileAccessError(path,
                              str(ex),
                              file_inclusion_chain,
                              section_name)
