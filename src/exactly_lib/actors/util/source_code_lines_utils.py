from typing import Sequence, List

from exactly_lib.section_document.syntax import is_empty_line, is_comment_line
from exactly_lib.test_case.phases.act import ActPhaseInstruction


def all_source_code_lines(instructions: Sequence[ActPhaseInstruction]) -> List[str]:
    ret_val = []
    for instruction in instructions:
        for line in instruction.source_code().lines:
            if _is_source_code_line(line):
                ret_val.append(line)
    return ret_val


def _is_source_code_line(line: str) -> bool:
    return not (is_empty_line(line) or is_comment_line(line))
