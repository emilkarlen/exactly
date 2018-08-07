import pathlib

from exactly_lib.section_document.source_location import FileLocationInfo, FileSystemLocationInfo

ARBITRARY_FS_LOCATION_INFO = FileSystemLocationInfo(
    FileLocationInfo(pathlib.Path.cwd())
)


def space_separator_instruction_name_extractor(line: str) -> str:
    return line.split(maxsplit=1)[0]
