from typing import Sequence, List

from exactly_lib.section_document.syntax import is_empty_or_comment_line
from exactly_lib.test_case.phases.act import ActPhaseInstruction


def all_source_code_lines(instructions: Sequence[ActPhaseInstruction]) -> List[str]:
    ret_val = []
    for instruction in instructions:
        for line in instruction.source_code().lines:
            if not is_empty_or_comment_line(line):
                ret_val.append(line)
    return ret_val


def all_source_code_lines_str(instructions: Sequence[ActPhaseInstruction]) -> str:
    lines = all_source_code_lines(instructions)
    return (
        '\n'.join(lines) + '\n'
        if lines
        else
        ''
    )
