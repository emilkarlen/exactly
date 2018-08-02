import pathlib

from exactly_lib.section_document.element_builder import SourceLocationInfo
from exactly_lib.section_document.parsing_configuration import FileSystemLocationInfo

ARBITRARY_FS_LOCATION_INFO = FileSystemLocationInfo(SourceLocationInfo(
    abs_path_of_dir_containing_file=pathlib.Path.cwd()))
