import pathlib

from exactly_lib.section_document.source_location import FileLocationInfo, SourceLocationInfo
from exactly_lib.util import line_source

_FL = FileLocationInfo(pathlib.Path('/'))


def single_line_sequence(line_number: int, line: str) -> SourceLocationInfo:
    return source_info_for_line_sequence(line_source.single_line_sequence(line_number, line))


def source_info_for_line_sequence(source: line_source.LineSequence) -> SourceLocationInfo:
    return _FL.source_location_info_for(source)
