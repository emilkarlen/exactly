import pathlib

from exactly_lib.section_document.parsing_configuration import FileSystemLocationInfo

ARBITRARY_FS_LOCATION_INFO = FileSystemLocationInfo(pathlib.Path.cwd())
