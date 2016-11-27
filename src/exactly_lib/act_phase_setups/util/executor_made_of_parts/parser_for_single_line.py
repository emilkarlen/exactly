import shlex

from exactly_lib.act_phase_setups.util.executor_made_of_parts.parts import Parser, ParseException
from exactly_lib.section_document.syntax import is_empty_line, is_comment_line
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.result import svh


class ParserForSingleLineUsingStandardSyntax(Parser):
    """
    A parser that fails if there is not one, and only one, line that is not
    empty and not a comment.

    :returns The single non-empty line
    """

    def apply(self, act_phase_instructions: list) -> str:
        return _parse_single_line(act_phase_instructions)


class ParserForSingleLineUsingStandardSyntaxSplitAccordingToShellSyntax(Parser):
    """
    A parser that fails if there is not one, and only one, line that is not
    empty and not a comment.

    :returns The single non-empty line, split according to shell syntax.
    """

    def apply(self, act_phase_instructions: list) -> list:
        single_line = _parse_single_line(act_phase_instructions)
        return shlex.split(single_line)


def _parse_single_line(act_phase_instructions: list) -> str:
    non_empty_lines = _all_source_code_lines(act_phase_instructions)
    if not non_empty_lines:
        raise ParseException(svh.new_svh_validation_error('No lines with source code found'))
    if len(non_empty_lines) > 1:
        raise ParseException(svh.new_svh_validation_error('More than one lines with source code found'))
    return non_empty_lines[0]


def _all_source_code_lines(act_phase_instructions) -> list:
    ret_val = []
    for instruction in act_phase_instructions:
        assert isinstance(instruction, ActPhaseInstruction)
        for line in instruction.source_code().lines:
            if _is_source_code_line(line):
                ret_val.append(line)
    return ret_val


def _is_source_code_line(line) -> bool:
    return not (is_empty_line(line) or is_comment_line(line))
