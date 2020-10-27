from typing import Tuple, Sequence

from exactly_lib.type_system.logic.line_matcher import LineMatcherLine
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def matches_line_matcher_model(n: int, contents: str) -> ValueAssertion[LineMatcherLine]:
    return asrt.and_([
        asrt.elem_at_index('line number', 0, asrt.equals(n)),
        asrt.elem_at_index('line contents', 1, asrt.equals(contents)),
    ])


def matches_line(n: int, full_contents: str) -> ValueAssertion[Tuple[str, LineMatcherLine]]:
    return asrt.and_([
        asrt.elem_at_index(
            'full line contents', 0, asrt.equals(full_contents)
        ),
        asrt.elem_at_index(
            'line matcher model', 1,
            matches_line_matcher_model(n, full_contents.rstrip('\n'))
        )
    ])


def matches_lines(first_line_num: int,
                  full_contents: Sequence[str],
                  ) -> ValueAssertion[Sequence[Tuple[str, LineMatcherLine]]]:
    return asrt.matches_sequence([
        matches_line(line_num, full_contents)
        for line_num, full_contents in enumerate(full_contents, start=first_line_num)
    ])
