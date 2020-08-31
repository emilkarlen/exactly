from typing import Sequence

from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.strings import WithToString


def sym_ref_cmd_line(symbol_name: WithToString, arguments: Sequence[WithToString] = ()) -> ArgumentElementsRenderer:
    return ab.sequence([symbol_name] + list(arguments))


def system_program_cmd_line(program_name: WithToString,
                            arguments: Sequence[WithToString] = ()) -> ArgumentElementsRenderer:
    return ab.sequence([program_name] + list(arguments))


def remaining_part_of_current_line_as_literal(remaining_part_of_current_line: str) -> ArgumentElementsRenderer:
    return ab.sequence([syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER,
                        remaining_part_of_current_line])
