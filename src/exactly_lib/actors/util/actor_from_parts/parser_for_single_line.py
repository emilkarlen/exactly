import shlex
from typing import Sequence

from exactly_lib.actors.util.actor_from_parts.parts import ExecutableObjectParser
from exactly_lib.actors.util.source_code_lines import all_source_code_lines
from exactly_lib.test_case.actor import ParseException
from exactly_lib.test_case.phases.act import ActPhaseInstruction


class ParserForSingleLineUsingStandardSyntax(ExecutableObjectParser):
    """
    A parser that fails if there is not one, and only one, line that is not
    empty and not a comment.

    :returns The single non-empty line
    """

    def apply(self, instructions: Sequence[ActPhaseInstruction]) -> str:
        return _parse_single_line(instructions)


class ParserForSingleLineUsingStandardSyntaxSplitAccordingToShellSyntax(ExecutableObjectParser):
    """
    A parser that fails if there is not one, and only one, line that is not
    empty and not a comment.

    :returns The single non-empty line, split according to shell syntax.
    """

    def apply(self, instructions: Sequence[ActPhaseInstruction]) -> list:
        single_line = _parse_single_line(instructions)
        return shlex.split(single_line)


def _parse_single_line(instructions: Sequence[ActPhaseInstruction]) -> str:
    non_empty_lines = all_source_code_lines(instructions)
    if not non_empty_lines:
        raise ParseException.of_str(_NO_SOURCE_LINES)
    if len(non_empty_lines) > 1:
        raise ParseException.of_str(_TOO_MANY_SOURCE_LINES)
    return non_empty_lines[0]


_NO_SOURCE_LINES = 'No lines with source code found'
_TOO_MANY_SOURCE_LINES = 'More than one line with source code found'
