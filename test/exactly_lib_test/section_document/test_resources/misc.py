import pathlib

from exactly_lib.section_document.parsing_configuration import FileSystemLocationInfo, SourceLocationInfo

ARBITRARY_FS_LOCATION_INFO = FileSystemLocationInfo(SourceLocationInfo(
    abs_path_of_dir_containing_file=pathlib.Path.cwd()))
