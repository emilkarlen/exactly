import pathlib

from exactly_lib.section_document.parse_source import ParseSource


def new_for_file(path: pathlib.Path) -> ParseSource:
    with path.open() as fo:
        contents = fo.read()
    return ParseSource(contents)
