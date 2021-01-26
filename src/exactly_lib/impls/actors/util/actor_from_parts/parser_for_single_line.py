from typing import Sequence

from exactly_lib.impls.actors.util.actor_from_parts.parts import ExecutableObjectParser
from exactly_lib.impls.actors.util.source_code_lines import all_source_code_lines__std_syntax
from exactly_lib.test_case.phases.act.actor import ParseException
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction


class ParserForSingleLineUsingStandardSyntax(ExecutableObjectParser):
    """
    A parser that fails if there is not one, and only one, line that is not
    empty and not a comment.

    :returns The single non-empty line
    """

    def apply(self, instructions: Sequence[ActPhaseInstruction]) -> str:
        return _parse_single_line(instructions)


def _parse_single_line(instructions: Sequence[ActPhaseInstruction]) -> str:
    non_empty_lines = all_source_code_lines__std_syntax(instructions)
    if not non_empty_lines:
        raise ParseException.of_str(_NO_SOURCE_LINES)
    if len(non_empty_lines) > 1:
        raise ParseException.of_str(_TOO_MANY_SOURCE_LINES)
    return non_empty_lines[0]


_NO_SOURCE_LINES = 'No lines with source code found'
_TOO_MANY_SOURCE_LINES = 'More than one line with source code found'
