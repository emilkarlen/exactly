from typing import List, Optional

from exactly_lib.definitions.formatting import SectionName
from exactly_lib.test_case.phase_identifier import Phase


class LineInFilePosition:
    def __init__(self,
                 file_name: str,
                 line_number: int):
        self.file_name = file_name
        self.line_number = line_number


class Reference:
    def __init__(self,
                 phase: Phase,
                 position_in_file: Optional[LineInFilePosition],
                 source_lines: List[str]):
        self.phase = phase
        self.position_in_file = position_in_file
        self.source_lines = source_lines

    def output_lines(self) -> List[str]:
        phase_header_lines = [
            'In ' + SectionName(self.phase.section_name).syntax
        ]

        position_lines = (
            []
            if self.position_in_file is None
            else [
                self.position_in_file.file_name + ', line ' + str(self.position_in_file.line_number)
            ]
        )
        source_lines = [
            INDENT + source_line
            for source_line in self.source_lines
        ]

        return phase_header_lines + position_lines + [''] + source_lines


INDENT = '  '
