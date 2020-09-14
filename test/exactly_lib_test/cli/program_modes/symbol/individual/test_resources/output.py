from typing import List, Optional

from exactly_lib.cli.program_modes.symbol.impl.reports import individual
from exactly_lib.definitions.formatting import SectionName
from exactly_lib.test_case.phase_identifier import Phase
from exactly_lib.type_system.value_type import ValueType
from exactly_lib_test.cli.program_modes.symbol.test_resources import output
from exactly_lib_test.test_resources.value_assertions import value_assertion_str as asrt_str
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


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
                '',
                self.position_in_file.file_name + ', line ' + str(self.position_in_file.line_number)
            ]
        )
        source_lines = [
            INDENT + source_line
            for source_line in self.source_lines
        ]

        return phase_header_lines + position_lines + [''] + source_lines


def definition_of_builtin_symbol(name: str,
                                 value_type: ValueType,
                                 num_refs: int) -> ValueAssertion[str]:
    summary_line = output.summary_of_single(output.SymbolSummary(name,
                                                                 value_type,
                                                                 num_refs))
    return asrt_str.begins_with(''.join([summary_line,
                                         '\n',
                                         MAJOR_BLOCKS_SEPARATOR,
                                         individual.BUILTIN_SYMBOL_DEFINITION_SOURCE_LINE]))


INDENT = '  '
MAJOR_BLOCKS_SEPARATOR = '\n\n'
