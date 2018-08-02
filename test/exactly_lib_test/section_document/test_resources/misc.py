import pathlib

from exactly_lib.section_document.source_location import FileLocationInfo, FileSystemLocationInfo

ARBITRARY_FS_LOCATION_INFO = FileSystemLocationInfo(FileLocationInfo(
    pathlib.Path.cwd(),
    abs_path_of_dir_containing_file=pathlib.Path.cwd()))
