import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.parse.expression import expression_parser as sut
from exactly_lib_test.section_document.test_resources import parse_source as asrt_source
from exactly_lib_test.test_case_utils.parse.expression.test_resources import ast
from exactly_lib_test.test_case_utils.parse.test_resources.source_case import SourceCase
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.quoting import surrounded_by_soft_quotes, surrounded_by_hard_quotes


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSingleSimpleExpression),
    ])


class Arrangement:
    def __init__(self,
                 grammar: sut.Grammar,
                 source: ParseSource):
        self.grammar = grammar
        self.source = source


class Expectation:
    def __init__(self,
                 expression: ast.Expr,
                 source: asrt.ValueAssertion):
        self.expression = expression
        self.source = source


class TestCaseBase(unittest.TestCase):
    def _check(self,
               arrangement: Arrangement,
               expectation: Expectation):
        actual = sut.parse_from_parse_source(arrangement.grammar,
                                             arrangement.source)
        self.assertEqual(expectation.expression,
                         actual,
                         'parsed expression')
        expectation.source.apply_with_message(self,
                                              arrangement.source,
                                              'source after parse')


class TestSingleSimpleExpression(TestCaseBase):
    def test_successful_parse_of_expr_sans_argument(self):
        space_after = '           '
        token_after = str(surrounded_by_hard_quotes('not an expression'))
        cases = [
            SourceCase(
                'first line is only simple expr',
                source=
                remaining_source('{simple_expr}'.format(
                    simple_expr=ast.SIMPLE_SANS_ARG,
                )),
                source_assertion=
                asrt_source.is_at_end_of_line(1)
            ),
            SourceCase(
                'first line is simple expr with space around',
                source=
                remaining_source('  {simple_expr}{space_after}'.format(
                    simple_expr=ast.SIMPLE_SANS_ARG,
                    space_after=space_after)),
                source_assertion=
                asrt_source.source_is_not_at_end(current_line_number=asrt.equals(1),
                                                 remaining_part_of_current_line=asrt.equals(space_after[1:]))
            ),
            SourceCase(
                'expression is followed by non-expression',
                source=
                remaining_source('{simple_expr} {token_after}'.format(
                    simple_expr=ast.SIMPLE_SANS_ARG,
                    token_after=token_after)),
                source_assertion=
                asrt_source.source_is_not_at_end(current_line_number=asrt.equals(1),
                                                 remaining_part_of_current_line=asrt.equals(token_after))
            ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                self._check(
                    Arrangement(
                        grammar=
                        ast.GRAMMAR_WITH_ALL_COMPONENTS,
                        source=
                        case.source),
                    Expectation(
                        expression=
                        ast.SimpleSansArg(),
                        source=
                        case.source_assertion,
                    )
                )

        self._check(
            Arrangement(
                grammar=
                ast.GRAMMAR_WITH_ALL_COMPONENTS,
                source=
                remaining_source(ast.SIMPLE_SANS_ARG)),
            Expectation(
                expression=
                ast.SimpleSansArg(),
                source=
                asrt_source.is_at_end_of_line(1),
            )
        )

    def test_successful_parse_of_expr_with_argument(self):
        the_argument = 'the-argument'
        space_after = '           '
        token_after = str(surrounded_by_hard_quotes('not an expression'))
        cases = [
            SourceCase(
                'first line is only simple expr',
                source=
                remaining_source('{simple_with_arg} {argument}'.format(
                    simple_with_arg=ast.SIMPLE_WITH_ARG,
                    argument=the_argument)),
                source_assertion=
                asrt_source.is_at_end_of_line(1)
            ),
            SourceCase(
                'first line is simple expr with space around',
                source=
                remaining_source('  {simple_with_arg}    {argument}{space_after}'.format(
                    simple_with_arg=ast.SIMPLE_WITH_ARG,
                    argument=the_argument,
                    space_after=space_after)),
                source_assertion=
                asrt_source.source_is_not_at_end(current_line_number=asrt.equals(1),
                                                 remaining_part_of_current_line=asrt.equals(space_after[1:]))
            ),
            SourceCase(
                'expression is followed by non-expression',
                source=
                remaining_source('  {simple_with_arg}    {argument} {token_after}'.format(
                    simple_with_arg=ast.SIMPLE_WITH_ARG,
                    argument=the_argument,
                    token_after=token_after)),
                source_assertion=
                asrt_source.source_is_not_at_end(current_line_number=asrt.equals(1),
                                                 remaining_part_of_current_line=asrt.equals(token_after))
            ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                self._check(
                    Arrangement(
                        grammar=
                        ast.GRAMMAR_WITH_ALL_COMPONENTS,
                        source=
                        case.source),
                    Expectation(
                        expression=
                        ast.SimpleWithArg(the_argument),
                        source=
                        case.source_assertion,
                    )
                )

    def test_fail(self):
        cases = [
            (
                'source is just space',
                remaining_source('   '),
            ),
            (
                'token is not the name of a simple expression',
                remaining_source(ast.NOT_A_SIMPLE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME),
            ),
            (
                'token is the name of a simple expression, but it is quoted/soft',
                remaining_source(str(surrounded_by_soft_quotes(ast.SIMPLE_SANS_ARG))),
            ),
            (
                'token is the name of a simple expression, but it is quoted/hard',
                remaining_source(str(surrounded_by_hard_quotes(ast.SIMPLE_SANS_ARG))),
            ),
            (
                'token is the name of a simple expression, but it is on the next line',
                remaining_source('',
                                 [ast.SIMPLE_SANS_ARG]),
            ),
        ]
        for case_name, source in cases:
            with self.subTest(case_name=case_name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_from_parse_source(ast.GRAMMAR_WITH_ALL_COMPONENTS,
                                                source)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
