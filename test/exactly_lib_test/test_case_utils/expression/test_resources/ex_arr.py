from typing import Optional

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_utils.expression import parser as sut
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case_utils.expression.test_resources import test_grammars as ast
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class Arrangement:
    def __init__(self,
                 grammar: sut.Grammar,
                 source: ParseSource,
                 must_be_on_current_line: bool = True):
        self.grammar = grammar
        self.source = source
        self.must_be_on_current_line = must_be_on_current_line


class Expectation:
    def __init__(self,
                 expression: ast.Expr,
                 source: ValueAssertion):
        self.expression = expression
        self.source = source


class SourceExpectation:
    def __init__(self,
                 current_line_number: int,
                 remaining_part_of_current_line: Optional[str],
                 ):
        self.current_line_number = current_line_number
        self.remaining_part_of_current_line = remaining_part_of_current_line

    @staticmethod
    def is_at_end_of_line(n: int) -> 'SourceExpectation':
        return SourceExpectation(n, None)

    @staticmethod
    def source_is_not_at_end(current_line_number: int,
                             remaining_part_of_current_line: str) -> 'SourceExpectation':
        return SourceExpectation(
            current_line_number,
            remaining_part_of_current_line,
        )

    def for_added_empty_first_line(self) -> 'SourceExpectation':
        return SourceExpectation(
            self.current_line_number + 1,
            self.remaining_part_of_current_line,
        )

    @property
    def assertion(self) -> ValueAssertion[ParseSource]:
        return (
            asrt_source.is_at_end_of_line(self.current_line_number)
            if self.remaining_part_of_current_line is None
            else
            asrt_source.source_is_not_at_end(
                current_line_number=asrt.equals(self.current_line_number),
                remaining_part_of_current_line=asrt.equals(self.remaining_part_of_current_line)
            )
        )


class SourceCase:
    def __init__(self,
                 name: str,
                 source: str,
                 expectation: SourceExpectation,
                 ):
        self.name = name
        self.source = source
        self.expectation = expectation

    @property
    def parse_source(self) -> ParseSource:
        return remaining_source(self.source)

    @property
    def assertion(self) -> ValueAssertion[ParseSource]:
        return self.expectation.assertion

    def for_added_empty_first_line(self) -> 'SourceCase':
        return SourceCase(
            self.name + ' / first line is empty',
            '\n' + self.source,
            self.expectation.for_added_empty_first_line()
        )
