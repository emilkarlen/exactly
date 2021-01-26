from typing import Sequence, List

from exactly_lib.section_document.syntax import is_empty_or_comment_line
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.util.str_ import misc_formatting


def all_source_code_lines(instructions: Sequence[ActPhaseInstruction]) -> List[str]:
    ret_val = []
    for instruction in instructions:
        ret_val += instruction.source_code().lines
    return ret_val


def all_source_code_lines__std_syntax(instructions: Sequence[ActPhaseInstruction]) -> List[str]:
    """
    :return: All lines that are neither empty or a comment (according to "std" syntax)
    """
    return [
        line
        for line in all_source_code_lines(instructions)
        if not is_empty_or_comment_line(line)
    ]


def all_source_code_lines_str__std_syntax(instructions: Sequence[ActPhaseInstruction]) -> str:
    return misc_formatting.lines_content(all_source_code_lines__std_syntax(instructions))
