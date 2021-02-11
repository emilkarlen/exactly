from typing import Sequence

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.str_ import misc_formatting
from exactly_lib_test.test_resources.source import layout
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.layout import LayoutSpec


def of_lines(on_separate_lines: Sequence[AbstractSyntax]) -> str:
    layout_spec = LayoutSpec.of_default()

    return misc_formatting.lines_content([
        syntax.tokenization().layout(layout_spec)
        for syntax in on_separate_lines
    ])


def formatting_cases(syntax: AbstractSyntax) -> Sequence[NameAndValue[str]]:
    tokens = syntax.tokenization()
    return [
        NameAndValue(layout_case.name,
                     tokens.layout(layout_case.value))
        for layout_case in layout.STANDARD_LAYOUT_SPECS
    ]
