from pathlib import Path
from typing import Sequence

from exactly_lib.section_document.exceptions import FileAccessError
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import SourceLocation
from exactly_lib.section_document.utils import new_for_file


def read_source_file(file_path: Path,
                     file_path_for_error_message: Path,
                     file_inclusion_chain: Sequence[SourceLocation]) -> ParseSource:
    try:
        return new_for_file(file_path)
    except OSError as ex:
        raise FileAccessError(file_path_for_error_message,
                              str(ex),
                              file_inclusion_chain)


def resolve_file_reference_relativity_root_dir(path_of_dir_containing_root_file: Path,
                                               file_ref_rel_root: Path,
                                               file_inclusion_chain: Sequence[SourceLocation]
                                               ) -> Path:
    try:
        return path_of_dir_containing_root_file.resolve()
    except RuntimeError as ex:
        raise FileAccessError(path_of_dir_containing_root_file,
                              str(ex),
                              file_inclusion_chain)
