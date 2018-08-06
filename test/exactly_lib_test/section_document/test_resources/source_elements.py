from pathlib import Path

from exactly_lib.section_document.source_location import SourceLocationPath, SourceLocation
from exactly_lib.util.line_source import single_line_sequence

SOURCE_LOCATION_PATH_WITH_INCLUSIONS_AND_FILE_NAMES = SourceLocationPath(
    SourceLocation(
        single_line_sequence(1, 'the line'),
        Path('src-file')),
    [
        SourceLocation(
            single_line_sequence(2, 'the other line'),
            Path('other src-file')),
    ]
)
