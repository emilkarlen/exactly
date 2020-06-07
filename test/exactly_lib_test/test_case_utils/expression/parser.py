import itertools
import unittest
from typing import Optional, Sequence, List

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_utils.expression import parser as sut
from exactly_lib.test_case_utils.expression.grammar import Grammar
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.string import StringFormatter
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source, source_of_lines, \
    remaining_source_string
from exactly_lib_test.test_case_utils.expression.test_resources import test_grammars as ast
from exactly_lib_test.test_case_utils.expression.test_resources.test_grammars import ComplexA, ComplexB, PrefixExprP
from exactly_lib_test.test_resources.test_utils import NArrEx
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.test_resources.quoting import surrounded_by_soft_quotes, surrounded_by_hard_quotes


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailuresCommonToAllGrammars),
        unittest.makeSuite(TestSingleSimpleExpression),
        unittest.makeSuite(TestSinglePrefixExpression),
        unittest.makeSuite(TestSingleRefExpression),
        unittest.makeSuite(TestComplexExpression),
        unittest.makeSuite(TestCombinedExpressions),
    ])


GRAMMARS = [
    NameAndValue(
        'sans complex expressions',
        ast.GRAMMAR_SANS_COMPLEX_EXPRESSIONS,
    ),
    NameAndValue(
        'with complex expressions',
        ast.GRAMMAR_WITH_ALL_COMPONENTS,
    ),
]


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


class TestCaseBase(unittest.TestCase):
    def _check(self,
               arrangement: Arrangement,
               expectation: Expectation):
        _check(self, arrangement, expectation)


class TestFailuresCommonToAllGrammars(TestCaseBase):
    def test(self):
        for grammar in GRAMMARS:
            cases = [
                NameAndValue(
                    'source is just space',
                    remaining_source('   '),
                ),
                NameAndValue(
                    'first token quoted/soft',
                    remaining_source(str(surrounded_by_soft_quotes('token'))),
                ),
                NameAndValue(
                    'first token quoted/hard',
                    remaining_source(str(surrounded_by_hard_quotes('token'))),
                ),
                NameAndValue(
                    'missing )',
                    remaining_source('( {simple} '.format(simple=ast.SIMPLE_SANS_ARG)),
                ),
            ]
            for case in cases:
                with self.subTest(grammar=grammar.name,
                                  case_name=case.name):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.parse_from_parse_source(grammar.value,
                                                    case.value)


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


class TestSingleSimpleExpression(TestCaseBase):
    def test_successful_parse_of_expr_sans_argument(self):
        space_after = '           '
        token_after = str(surrounded_by_hard_quotes('not an expression'))

        format_map = {
            'simple_expr': ast.SIMPLE_SANS_ARG,
            'space_after': space_after,
            'token_after': token_after,
        }

        def source(s: str) -> str:
            return s.format_map(format_map)

        cases = [
            SourceCase(
                'first line is only simple expr',
                source('{simple_expr}'),
                SourceExpectation.is_at_end_of_line(1)
            ),
            SourceCase(
                'first line is simple expr with space around',
                source('  {simple_expr}{space_after}'),
                SourceExpectation.source_is_not_at_end(current_line_number=1,
                                                       remaining_part_of_current_line=space_after[1:])
            ),
            SourceCase(
                'expression is followed by non-expression',
                source('{simple_expr} {token_after}'),
                SourceExpectation.source_is_not_at_end(current_line_number=1,
                                                       remaining_part_of_current_line=token_after)
            ),
            SourceCase(
                '( simple )',
                source('( {simple_expr} )'),
                SourceExpectation.is_at_end_of_line(1),
            ),
            SourceCase(
                '( simple ) followed by non-expression',
                source('( {simple_expr} ) {token_after}'),
                SourceExpectation.source_is_not_at_end(current_line_number=1,
                                                       remaining_part_of_current_line=token_after),
            ),
            SourceCase(
                '( ( simple ) )',
                source('( ( {simple_expr} ) )'),
                SourceExpectation.is_at_end_of_line(1),
            ),
        ]
        # ACT & ASSERT #
        _check_with_must_be_on_current_line_variants(self, ast.SimpleSansArg(), GRAMMARS, cases)

    def test_successful_parse_of_expr_with_argument(self):
        # ARRANGE #

        the_argument = 'the-argument'
        space_after = '           '
        token_after = str(surrounded_by_hard_quotes('not an expression'))

        format_map = {
            'simple_with_arg': ast.SIMPLE_WITH_ARG,
            'argument': the_argument,
            'space_after': space_after,
            'token_after': token_after,
        }

        def source(s: str) -> str:
            return s.format_map(format_map)

        cases = [
            SourceCase(
                'first line is only simple expr',
                source('{simple_with_arg} {argument}'),
                SourceExpectation.is_at_end_of_line(1)
            ),
            SourceCase(
                'first line is simple expr with space around',
                source('  {simple_with_arg}    {argument}{space_after}'),
                SourceExpectation.source_is_not_at_end(current_line_number=1,
                                                       remaining_part_of_current_line=space_after[1:])
            ),
            SourceCase(
                'expression is followed by non-expression',
                source('  {simple_with_arg}    {argument} {token_after}'),
                SourceExpectation.source_is_not_at_end(current_line_number=1,
                                                       remaining_part_of_current_line=token_after)
            ),
            SourceCase(
                '( simple )',
                source('( {simple_with_arg} {argument} )'),
                SourceExpectation.is_at_end_of_line(1),
            ),
            SourceCase(
                'simple, within parenthesis, with tokens on separate lines',
                source('( \n {simple_with_arg} \n {argument} \n )'),
                SourceExpectation.is_at_end_of_line(4),
            ),
            SourceCase(
                'simple, within parenthesis, with expression tokens on separate lines, followed by non-expression',
                source('( \n {simple_with_arg} \n {argument} \n ) {token_after}'),
                SourceExpectation.source_is_not_at_end(current_line_number=4,
                                                       remaining_part_of_current_line=token_after),
            ),
            SourceCase(
                '( ( simple ) )',
                source('( ( {simple_with_arg} {argument} ) )'),
                SourceExpectation.is_at_end_of_line(1),
            ),
        ]

        # ACT & ASSERT #

        _check_with_must_be_on_current_line_variants(self,
                                                     ast.SimpleWithArg(the_argument),
                                                     GRAMMARS,
                                                     cases)

    def test_fail__expr_on_following_line_is_accepted(self):
        cases = [
            NameAndValue(
                'token is not the name of a simple expression',
                ast.NOT_A_SIMPLE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME,
            ),
            NameAndValue(
                'token is the name of a simple expression, but it is quoted/soft',
                str(surrounded_by_soft_quotes(ast.SIMPLE_SANS_ARG)),
            ),
            NameAndValue(
                'token is the name of a simple expression, but it is quoted/hard',
                str(surrounded_by_hard_quotes(ast.SIMPLE_SANS_ARG)),
            ),
        ]
        for grammar_description, grammar in GRAMMARS:
            for case in cases:
                # Source is on first line
                for must_be_on_current_line in [False, True]:
                    with self.subTest(grammar=grammar_description,
                                      case_name=case.name,
                                      source='is on first line',
                                      must_be_on_current_line=must_be_on_current_line):
                        # ACT & ASSERT #
                        parse_source = remaining_source_string(case.value)
                        with self.assertRaises(SingleInstructionInvalidArgumentException):
                            sut.parse_from_parse_source(grammar,
                                                        parse_source,
                                                        must_be_on_current_line=must_be_on_current_line)
                # Source is not on first line
                with self.subTest(grammar=grammar_description,
                                  case_name=case.name,
                                  source='is not on first line',
                                  must_be_on_current_line=must_be_on_current_line):
                    parse_source = remaining_source_string('\n' + case.value)
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.parse_from_parse_source(grammar,
                                                    parse_source,
                                                    must_be_on_current_line=False)

    def test_fail__must_be_on_current_line(self):
        for grammar_description, grammar in GRAMMARS:
            cases = [
                NameAndValue(
                    'token is not the name of a simple expression',
                    remaining_source('',
                                     [ast.NOT_A_SIMPLE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME],
                                     ),
                ),
                NameAndValue(
                    'token is the name of a simple expression, but it is quoted/soft',
                    remaining_source('',
                                     [str(surrounded_by_soft_quotes(ast.SIMPLE_SANS_ARG))]
                                     ),
                ),
                NameAndValue(
                    'token is the name of a simple expression, but it is quoted/hard',
                    remaining_source('',
                                     [str(surrounded_by_hard_quotes(ast.SIMPLE_SANS_ARG))]
                                     ),
                ),
                NameAndValue(
                    'token is the name of a simple expression, but it is on the next line',
                    remaining_source('',
                                     [ast.SIMPLE_SANS_ARG]),
                ),
            ]
            for case in cases:
                with self.subTest(grammar=grammar_description,
                                  case_name=case.name):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.parse_from_parse_source(grammar,
                                                    case.value,
                                                    must_be_on_current_line=True)


class TestSinglePrefixExpression(TestCaseBase):
    PREFIX_OPERATORS = [
        (
            ast.PREFIX_P,
            ast.PrefixExprP,
        ),
        (
            ast.PREFIX_Q,
            ast.PrefixExprQ,
        ),
    ]

    def test_successful_parse_with_simple_expr(self):

        space_after = '           '
        token_after = str(surrounded_by_hard_quotes('not an expression'))

        simple_expr = ast.SimpleSansArg()
        simple_expr_src = ast.SIMPLE_SANS_ARG

        def cases_for_operator(the_prefix_operator: str) -> List[SourceCase]:
            sf = StringFormatter({
                'op': the_prefix_operator,
                'simple_expr': simple_expr_src,
                'space_after': space_after,
                'token_after': token_after,
            })
            return [
                SourceCase(
                    'first line is only simple expr',
                    sf.format('{op} {simple_expr}'),
                    SourceExpectation.is_at_end_of_line(1)
                ),
                SourceCase(
                    'first line is simple expr with space around',
                    sf.format(' {op}  {simple_expr}{space_after}'),
                    SourceExpectation.source_is_not_at_end(current_line_number=1,
                                                           remaining_part_of_current_line=space_after[1:])
                ),
                SourceCase(
                    'expression is followed by non-expression',
                    sf.format('{op} {simple_expr} {token_after}'),
                    SourceExpectation.source_is_not_at_end(current_line_number=1,
                                                           remaining_part_of_current_line=token_after)
                ),
                SourceCase(
                    '( op simple )',
                    sf.format('( {op} {simple_expr} )'),
                    SourceExpectation.is_at_end_of_line(1),
                ),
                SourceCase(
                    'op ( simple )',
                    sf.format('{op} ( {simple_expr} )'),
                    SourceExpectation.is_at_end_of_line(1),
                ),
                SourceCase(
                    'no source after operator, but expr on following line',
                    sf.format('{op}\n{simple_expr}'),
                    SourceExpectation.is_at_end_of_line(2),
                ),
            ]

        operator_cases = [
            (prefix_operator,
             mk_prefix_expr(simple_expr),
             cases_for_operator(prefix_operator))
            for prefix_operator, mk_prefix_expr in self.PREFIX_OPERATORS
        ]

        for grammar in GRAMMARS:
            for operator_case in operator_cases:
                cases = _current_line_case_variants_for_grammar(operator_case[1],
                                                                grammar.value,
                                                                operator_case[2])
                for case in cases:
                    with self.subTest(grammar=grammar.name,
                                      prefix_operator=operator_case[0],
                                      name=case.name):
                        self._check(
                            case.arrangement,
                            case.expectation)

    def test_successful_parse_with_complex_expressions(self):
        s = ast.SimpleSansArg()
        cases = [
            NArrEx(
                'prefix operator binds to following simple expression (single complex ops)',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('{p_op} {s}  {bin_op}  {s}  {bin_op}  {p_op} {s}'.format(
                        s=ast.SIMPLE_SANS_ARG,
                        p_op=ast.PREFIX_P,
                        bin_op=ast.COMPLEX_A,
                    )),
                ),
                Expectation(
                    expression=ComplexA([PrefixExprP(s), s, PrefixExprP(s)]),
                    source=asrt_source.is_at_end_of_line(1),
                ),
            ),
            NArrEx(
                'prefix operator binds to following simple expression (different complex ops)',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('{p_op} {s}  {bin_op_a}  {s}  {bin_op_b}  {p_op} {s}'.format(
                        s=ast.SIMPLE_SANS_ARG,
                        p_op=ast.PREFIX_P,
                        bin_op_a=ast.COMPLEX_A,
                        bin_op_b=ast.COMPLEX_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME,
                    )),
                ),
                Expectation(
                    expression=ComplexB([ComplexA([PrefixExprP(s), s]), PrefixExprP(s)]),
                    source=asrt_source.is_at_end_of_line(1),
                ),
            ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                self._check(
                    case.arrangement,
                    case.expectation
                )

    def test_fail(self):
        for grammar_description, grammar in GRAMMARS:
            for prefix_operator, mk_prefix_expr in self.PREFIX_OPERATORS:
                cases = [
                    NameAndValue(
                        'no source after operator',
                        remaining_source(prefix_operator),
                    ),
                    NameAndValue(
                        'operator followed by non-expression',
                        remaining_source('{op} {non_expr}'.format(
                            op=prefix_operator,
                            non_expr=str(surrounded_by_soft_quotes(ast.SIMPLE_SANS_ARG)))),
                    ),
                ]
                for case in cases:
                    with self.subTest(grammar=grammar_description,
                                      prefix_operator=prefix_operator,
                                      case_name=case.name):
                        with self.assertRaises(SingleInstructionInvalidArgumentException):
                            sut.parse_from_parse_source(grammar,
                                                        case.value)


class TestSingleRefExpression(TestCaseBase):
    def test_successful_parse(self):
        symbol_name = 'the_symbol_name'
        space_after = '           '
        token_after = str(surrounded_by_hard_quotes('not an expression'))
        symbol_ref_syntax_cases = [
            NameAndValue('plain',
                         symbol_name,
                         ),
            NameAndValue('reference syntax',
                         symbol_reference_syntax_for_name(symbol_name),
                         ),
        ]

        def cases_for_symbol_syntax(symbol_reference: NameAndValue[str]) -> List[SourceCase]:
            sf = StringFormatter({
                'symbol_name': symbol_reference.value,
                'space_after': space_after,
                'token_after': token_after,
            })

            def source(template: str) -> str:
                return sf.format(template)

            def name(case: str) -> str:
                return 'symbol_syntax={} / {}'.format(
                    symbol_reference.name,
                    case
                )

            return [
                SourceCase(
                    name('first line is only simple expr'),
                    source('{symbol_name}'),
                    SourceExpectation.is_at_end_of_line(1)
                ),
                SourceCase(
                    name('first line is simple expr with space around'),
                    source('  {symbol_name}{space_after}'),
                    SourceExpectation.source_is_not_at_end(current_line_number=1,
                                                           remaining_part_of_current_line=space_after[1:])
                ),
                SourceCase(
                    name('expression is followed by non-expression'),
                    source('{symbol_name} {token_after}'),
                    SourceExpectation.source_is_not_at_end(current_line_number=1,
                                                           remaining_part_of_current_line=token_after)
                ),
            ]

        source_cases = list(
            itertools.chain.from_iterable([
                cases_for_symbol_syntax(symbol_ref_syntax)
                for symbol_ref_syntax in symbol_ref_syntax_cases
            ])
        )

        _check_with_must_be_on_current_line_variants(
            self,
            expected_expression=ast.RefExpr(symbol_name),
            grammars=GRAMMARS,
            original_source_cases=source_cases
        )

    def test_token_SHOULD_be_interpreted_as_sym_ref_WHEN_sym_ref_syntax_is_used_for_existing_primitive(self):
        for grammar_description, grammar in GRAMMARS:
            with self.subTest(grammar=grammar_description):
                self._check(
                    Arrangement(
                        grammar=grammar,
                        source=remaining_source(
                            symbol_reference_syntax_for_name(ast.SIMPLE_SANS_ARG)
                        ),
                    ),
                    Expectation(
                        expression=ast.RefExpr(ast.SIMPLE_SANS_ARG),
                        source=asrt_source.is_at_end_of_line(1),
                    )
                )

    def test_fail(self):
        symbol_name = 'the_symbol_name'
        for grammar_description, grammar in GRAMMARS:
            cases = [
                NameAndValue(
                    'symbol name is quoted',
                    remaining_source(str(surrounded_by_hard_quotes(symbol_name))),
                ),
                NameAndValue(
                    'symbol reference syntax with invalid symbol name character: space',
                    remaining_source(symbol_reference_syntax_for_name('the symbol')),
                ),
                NameAndValue(
                    'symbol reference syntax with invalid symbol name character: &',
                    remaining_source(symbol_reference_syntax_for_name('the&symbol')),
                ),
            ]
            for case in cases:
                with self.subTest(grammar=grammar_description,
                                  case_name=case.name):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.parse_from_parse_source(grammar,
                                                    case.value)


class TestComplexExpression(unittest.TestCase):
    def test_success_of_single_operator(self):
        valid_simple_expressions = [
            (
                '{simple_expression}'.format(simple_expression=ast.SIMPLE_SANS_ARG),
                ast.SimpleSansArg()
            ),
            (
                '{simple_expression_name} {argument}'.format(
                    simple_expression_name=ast.SIMPLE_WITH_ARG,
                    argument='simple-expr-argument'),
                ast.SimpleWithArg('simple-expr-argument')
            ),

        ]
        operators = [
            (
                ast.COMPLEX_A,
                ast.ComplexA,
            ),
            (
                ast.COMPLEX_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME,
                ast.ComplexB,
            ),
        ]

        def source_cases_for_expressions(simple_expr: str,
                                         operator: str) -> List[SourceCase]:
            sf = StringFormatter({
                'simple_expr': simple_expr,
                'operator': operator,
                'quoted_operator': surrounded_by_soft_quotes(operator_source),
                'space_after': '           ',
                'quoted_string': surrounded_by_hard_quotes('quoted string'),

            })

            def source(template: str) -> str:
                return sf.format(template)

            return [
                SourceCase(
                    'first line is just complex expr',
                    source('{simple_expr} {operator} {simple_expr}'),
                    SourceExpectation.is_at_end_of_line(1)
                ),
                SourceCase(
                    'first line is complex expr, followed by space',
                    source('{simple_expr} {operator} {simple_expr}{space_after}'),
                    SourceExpectation.source_is_not_at_end(
                        current_line_number=1,
                        remaining_part_of_current_line=sf.format('{space_after}')[1:])
                ),
                SourceCase(
                    'complex expr followed by non-operator',
                    source('{simple_expr} {operator} {simple_expr} {quoted_string}'),
                    SourceExpectation.source_is_not_at_end(
                        current_line_number=1,
                        remaining_part_of_current_line=sf.format('{quoted_string}'))
                ),
                SourceCase(
                    'complex expr followed by simple expression',
                    source('{simple_expr} {operator} {simple_expr} {simple_expr}'),
                    SourceExpectation.source_is_not_at_end(
                        current_line_number=1,
                        remaining_part_of_current_line=sf.format('{simple_expr}'))
                ),
                SourceCase(
                    'complex expr followed by quoted operator',
                    source('{simple_expr} {operator} {simple_expr} {quoted_operator}'),
                    SourceExpectation.source_is_not_at_end(
                        current_line_number=1,
                        remaining_part_of_current_line=sf.format('{quoted_operator}'))
                ),
                SourceCase(
                    'first line is just complex expr: inside ()',
                    source('( {simple_expr} {operator} {simple_expr} )'),
                    SourceExpectation.is_at_end_of_line(1)
                ),
                SourceCase(
                    'first simple expr inside ()',
                    source('( {simple_expr} ) {operator} {simple_expr}'),
                    SourceExpectation.is_at_end_of_line(1)
                ),
                SourceCase(
                    'second simple expr inside ()',
                    source('{simple_expr} {operator} ( {simple_expr} )'),
                    SourceExpectation.is_at_end_of_line(1)
                ),
                SourceCase(
                    'second expr on following line',
                    source('{simple_expr} {operator}\n{simple_expr}'),
                    SourceExpectation.is_at_end_of_line(2)
                ),
            ]

        for valid_simple_expr_source, expected_simple_expr in valid_simple_expressions:
            for operator_source, operator_constructor in operators:
                expected_expression = operator_constructor([expected_simple_expr,
                                                            expected_simple_expr])
                source_cases = source_cases_for_expressions(valid_simple_expr_source, operator_source)
                cases = _current_line_case_variants_for_grammar(expected_expression,
                                                                ast.GRAMMAR_WITH_ALL_COMPONENTS,
                                                                source_cases)

                for case in cases:
                    with self.subTest(name=case.name,
                                      operator_source=operator_source,
                                      valid_simple_expr_source=valid_simple_expr_source):
                        _check(self,
                               case.arrangement,
                               case.expectation)

    def test_success_of_expression_within_parentheses(self):
        s = ast.SimpleSansArg()
        cases = [
            NArrEx(
                'parentheses around first expr to make nested expr instead of "linear" args to op',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('( {s} {op}  {s} ) {op} {s}'.format(
                        s=ast.SIMPLE_SANS_ARG,
                        op=ast.COMPLEX_A,
                    )),
                ),
                Expectation(
                    expression=ComplexA([ComplexA([s, s]), s]),
                    source=asrt_source.is_at_end_of_line(1),
                ),
            ),
            NArrEx(
                'parentheses around final (second) expr to make first op have precedence',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('{s} {op} ( {s} {op} {s} )'.format(
                        s=ast.SIMPLE_SANS_ARG,
                        op=ast.COMPLEX_A,
                    )),
                ),
                Expectation(
                    expression=ComplexA([s, ComplexA([s, s])]),
                    source=asrt_source.is_at_end_of_line(1),
                ),
            ),
            NArrEx(
                '"linear" (sequence) of OPA, by embedding OPB inside parentheses',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('{s} {op_a} ( {s} {op_b} {s} ) {op_a} {s}'.format(
                        s=ast.SIMPLE_SANS_ARG,
                        op_a=ast.COMPLEX_A,
                        op_b=ast.COMPLEX_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME,
                    )),
                ),
                Expectation(
                    expression=ComplexA([s, ComplexB([s, s]), s]),
                    source=asrt_source.is_at_end_of_line(1),
                ),
            ),
            NArrEx(
                'parentheses around expr should allow binary operator to be on separate lines',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=source_of_lines([
                        '(',
                        ast.SIMPLE_SANS_ARG,
                        ast.COMPLEX_A,
                        ast.SIMPLE_SANS_ARG,
                        ')',
                    ]),
                ),
                Expectation(
                    expression=ComplexA([s, s]),
                    source=asrt_source.is_at_end_of_line(5),
                ),
            ),

        ]
        for case in cases:
            with self.subTest(name=case.name):
                _check(self,
                       case.arrangement,
                       case.expectation
                       )

    def test_success_of_expression_within_parentheses_spanning_several_lines(self):
        s = ast.SimpleSansArg()
        cases = [
            NArrEx(
                'simple expr and ) on following line',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('(',
                                            ['{s} )'.format(s=ast.SIMPLE_SANS_ARG)]),
                ),
                Expectation(
                    expression=s,
                    source=asrt_source.is_at_end_of_line(2),
                ),
            ),
            NArrEx(
                'simple expr and ) on following line, followed by non-expr',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('(',
                                            ['{s} ) non-expr'.format(s=ast.SIMPLE_SANS_ARG)]),
                ),
                Expectation(
                    expression=s,
                    source=asrt_source.source_is_not_at_end(current_line_number=asrt.equals(2),
                                                            remaining_part_of_current_line=asrt.equals('non-expr')),
                ),
            ),
            NArrEx(
                'simple expr with ) on following line',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('( {s}'.format(s=ast.SIMPLE_SANS_ARG),
                                            [' )']),
                ),
                Expectation(
                    expression=s,
                    source=asrt_source.is_at_end_of_line(2),
                ),
            ),
            NArrEx(
                'simple expr with ) on following line, and non-expr on line after that',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('( {s}'.format(s=ast.SIMPLE_SANS_ARG),
                                            [' )',
                                             'non-expr']),
                ),
                Expectation(
                    expression=s,
                    source=asrt_source.is_at_end_of_line(2),
                ),
            ),
            NArrEx(
                'binary op with only ( on first line',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('(',
                                            [' {s} {op} {s} )'.format(s=ast.SIMPLE_SANS_ARG,
                                                                      op=ast.COMPLEX_A)
                                             ]),
                ),
                Expectation(
                    expression=ComplexA([s, s]),
                    source=asrt_source.is_at_end_of_line(2),
                ),
            ),
            NArrEx(
                'binary op with ) on following line',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('( {s} {op} {s}'.format(s=ast.SIMPLE_SANS_ARG,
                                                                    op=ast.COMPLEX_A),
                                            [' ) ']),
                ),
                Expectation(
                    expression=ComplexA([s, s]),
                    source=asrt_source.is_at_end_of_line(2),
                ),
            ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                _check(self,
                       case.arrangement,
                       case.expectation
                       )

    def test_fail_parse_of_complex_expression(self):
        # ARRANGE #
        valid_simple_expressions = [
            '{simple_expression}'.format(simple_expression=ast.SIMPLE_SANS_ARG),
            '{simple_expression_name} {argument}'.format(
                simple_expression_name=ast.SIMPLE_WITH_ARG,
                argument='simple-expr-argument'),

        ]
        operators = [ast.COMPLEX_A,
                     ast.COMPLEX_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME]

        def cases_for(simple_expr: str, the_operator: str) -> List[NameAndValue[str]]:
            sf = StringFormatter({
                'simple_expr': simple_expr,
                'operator': the_operator,
                'non_expr': ast.NOT_A_SIMPLE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME,

            })

            return [
                NameAndValue(
                    'operator not followed by expression',
                    sf.format('{simple_expr} {operator}'),
                ),
                NameAndValue(
                    'operator followed by non-expression',
                    sf.format('{simple_expr} {operator} {non_expr}'),
                ),
                NameAndValue(
                    'operator followed by non-expression/two operators',
                    sf.format('{simple_expr} {operator} {simple_expr} {operator} {non_expr}'),
                ),
                NameAndValue(
                    '( at start of expr: missing )',
                    sf.format('( {simple_expr} {operator} {simple_expr} '),
                ),
                NameAndValue(
                    '( in middle of expr: missing )',
                    sf.format('( {simple_expr} {operator} ( {simple_expr} '),
                ),
            ]

        for valid_simple_expr in valid_simple_expressions:
            for operator in operators:
                cases = cases_for(valid_simple_expr, operator)
                # With source on first line
                for must_be_on_current_line in [False, True]:
                    for case in cases:
                        with self.subTest(case_name=case.name,
                                          operator=operator,
                                          valid_simple_expr=valid_simple_expr,
                                          source='appears on first line',
                                          must_be_on_current_line=must_be_on_current_line):
                            # ACT & ASSERT #
                            with self.assertRaises(SingleInstructionInvalidArgumentException):
                                sut.parse_from_parse_source(ast.GRAMMAR_WITH_ALL_COMPONENTS,
                                                            remaining_source_string(case.value),
                                                            must_be_on_current_line=must_be_on_current_line)
                # With source not on first line
                for case in cases:
                    with self.subTest(case_name=case.name,
                                      operator=operator,
                                      valid_simple_expr=valid_simple_expr,
                                      source='appears not on first line',
                                      must_be_on_current_line=must_be_on_current_line):
                        parse_source = remaining_source_string('\n' + case.value)
                        # ACT & ASSERT #
                        with self.assertRaises(SingleInstructionInvalidArgumentException):
                            sut.parse_from_parse_source(ast.GRAMMAR_WITH_ALL_COMPONENTS,
                                                        parse_source,
                                                        must_be_on_current_line=False)


class TestCombinedExpressions(TestCaseBase):
    def test__inside_parentheses__simple_recursive_followed_by_binary_op_on_following_line(self):
        s = ast.SimpleSansArg()

        expected = ast.ComplexA([ast.SimpleRecursive(s), s])

        arguments = '( \n {r} {s} \n {op_a} \n {s} \n )'.format(
            r=ast.SIMPLE_RECURSIVE,
            s=ast.SIMPLE_SANS_ARG,
            op_a=ast.COMPLEX_A,
        )

        self._check(
            Arrangement(
                grammar=
                ast.GRAMMAR_WITH_ALL_COMPONENTS,
                source=
                remaining_source(arguments)),
            Expectation(
                expression=
                expected,
                source=
                asrt_source.is_at_end_of_line(5),
            )
        )

    def test__inside_parentheses__simple_recursive_followed_by_binary_op_on_same_line(self):
        s = ast.SimpleSansArg()

        expected = ast.SimpleRecursive(ast.ComplexA([s, s]))
        # TODO want this to be same as above - fix with precedences

        arguments = '( \n {r} {s} {op_a} \n {s} \n )'.format(
            r=ast.SIMPLE_RECURSIVE,
            s=ast.SIMPLE_SANS_ARG,
            op_a=ast.COMPLEX_A,
        )

        self._check(
            Arrangement(
                grammar=
                ast.GRAMMAR_WITH_ALL_COMPONENTS,
                source=
                remaining_source(arguments)),
            Expectation(
                expression=
                expected,
                source=
                asrt_source.is_at_end_of_line(4),
            )
        )

    def test__simple_recursive_followed_by_binary_op_on_same_line(self):
        s = ast.SimpleSansArg()

        expected = ast.SimpleRecursive(ast.ComplexA([s, s]))

        arguments = '{r} {s} {op_a} {s}'.format(
            r=ast.SIMPLE_RECURSIVE,
            s=ast.SIMPLE_SANS_ARG,
            op_a=ast.COMPLEX_A,
        )

        self._check(
            Arrangement(
                grammar=
                ast.GRAMMAR_WITH_ALL_COMPONENTS,
                source=
                remaining_source(arguments)),
            Expectation(
                expression=
                expected,
                source=
                asrt_source.is_at_end_of_line(1),
            )
        )

    def test_combined_expression_with_single_simple_expr(self):
        # [ [ [ s A s ] B s B  s ] A s ]

        s = ast.SimpleSansArg()

        op_sequence_1 = ast.ComplexA([s, s])
        op_sequence_2 = ast.ComplexB([op_sequence_1, s, s])
        expected = ast.ComplexA([op_sequence_2, s])

        arguments = '{s} {op_a} {s} {op_b} {s} {op_b} {s} {op_a} {s}'.format(
            op_a=ast.COMPLEX_A,
            op_b=ast.COMPLEX_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME,
            s=ast.SIMPLE_SANS_ARG,
        )

        self._check(
            Arrangement(
                grammar=
                ast.GRAMMAR_WITH_ALL_COMPONENTS,
                source=
                remaining_source(arguments)),
            Expectation(
                expression=
                expected,
                source=
                asrt_source.is_at_end_of_line(1),
            )
        )

    def test_combined_expression_sans_parentheses(self):
        # [ [ [ ref1 OPA s ] OPB s OPB ref2 ] OPA s_x OPA ref3 ]

        ref_1 = ast.RefExpr('symbol_1')
        ref_2 = ast.RefExpr('symbol_2')
        ref_3 = ast.RefExpr('symbol_3')

        s = ast.SimpleSansArg()

        s_x = ast.SimpleWithArg('X')

        e1 = ast.ComplexA([
            ref_1,
            s,
        ])
        e2 = ast.ComplexB([
            e1,
            s,
            ref_2,
        ])
        expected = ast.ComplexA([
            e2,
            s_x,
            ref_3,
        ])

        argument_string = '{ref_1} {op_a} {s} {op_b} {s} {op_b} {ref_2} {op_a} {s_w_arg} {x} {op_a} {ref_3}'.format(
            s=ast.SIMPLE_SANS_ARG,
            ref_1=ref_1.symbol_name,
            ref_2=ref_2.symbol_name,
            ref_3=ref_3.symbol_name,
            op_a=ast.COMPLEX_A,
            op_b=ast.COMPLEX_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME,
            s_w_arg=ast.SIMPLE_WITH_ARG,
            x=s_x.argument,

        )
        self._check(
            Arrangement(
                grammar=
                ast.GRAMMAR_WITH_ALL_COMPONENTS,
                source=
                remaining_source(argument_string)),
            Expectation(
                expression=
                expected,
                source=
                asrt_source.is_at_end_of_line(1),
            )
        )

    def test_combined_expression_with_parentheses(self):
        #  ref1 OPA ( s OPB s_x OPB ref2 ) OPB s_y

        ref_1 = ast.RefExpr('symbol_1')
        ref_2 = ast.RefExpr('symbol_2')
        ref_3 = ast.RefExpr('symbol_3')

        s = ast.SimpleSansArg()

        s_x = ast.SimpleWithArg('X')
        s_y = ast.SimpleWithArg('Y')

        expected = ComplexB([
            ComplexA([
                ref_1,
                ComplexB([s, s_x, ref_2])
            ]),
            s_y,
        ])

        argument_string = '{ref_1} {op_a} ( {s} {op_b} {s_w_arg} {x} {op_b} {ref_2} ) {op_b} {s_w_arg} {y}'.format(
            s=ast.SIMPLE_SANS_ARG,
            ref_1=ref_1.symbol_name,
            ref_2=ref_2.symbol_name,
            ref_3=ref_3.symbol_name,
            op_a=ast.COMPLEX_A,
            op_b=ast.COMPLEX_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME,
            s_w_arg=ast.SIMPLE_WITH_ARG,
            x=s_x.argument,
            y=s_y.argument,

        )
        self._check(
            Arrangement(
                grammar=
                ast.GRAMMAR_WITH_ALL_COMPONENTS,
                source=
                remaining_source(argument_string)),
            Expectation(
                expression=
                expected,
                source=
                asrt_source.is_at_end_of_line(1),
            )
        )


def _check(put: unittest.TestCase,
           arrangement: Arrangement,
           expectation: Expectation):
    actual = sut.parse_from_parse_source(arrangement.grammar,
                                         arrangement.source,
                                         arrangement.must_be_on_current_line)
    if expectation.expression != actual:
        put.fail('Unexpected expression.\nExpected: {}\nActual  : {}'.format(
            str(expectation.expression),
            str(actual),
        ))
    put.assertEqual(expectation.expression,
                    actual,
                    'parsed expression: ' + str(actual))
    expectation.source.apply_with_message(put,
                                          arrangement.source,
                                          'source after parse')


def _current_line_case_variants_for_grammar(expected_expression: ast.Expr,
                                            grammar: Grammar,
                                            source_cases: Sequence[SourceCase],
                                            ) -> List[NArrEx[Arrangement, Expectation]]:
    ret_val = [
        NArrEx(
            the_source_case.name + ' / must_be_on_current_line=True',
            Arrangement(
                grammar=grammar,
                source=the_source_case.parse_source,
                must_be_on_current_line=True,
            ),
            Expectation(
                expression=expected_expression,
                source=the_source_case.assertion,
            )
        )
        for the_source_case in source_cases
    ]

    ret_val += [
        NArrEx(
            the_source_case.name + ' / must_be_on_current_line=False',
            Arrangement(
                grammar=grammar,
                source=the_source_case.parse_source,
                must_be_on_current_line=False,
            ),
            Expectation(
                expression=expected_expression,
                source=the_source_case.assertion,
            )
        )
        for the_source_case in source_cases
    ]

    ret_val += [
        _for_added_empty_first_line(expected_expression, grammar, the_source_case)
        for the_source_case in source_cases
    ]

    return ret_val


def _for_added_empty_first_line(expected_expression: ast.Expr,
                                the_grammar: Grammar,
                                src_case: SourceCase) -> NArrEx[Arrangement, Expectation]:
    case_for_empty_first_line = src_case.for_added_empty_first_line()
    return NArrEx(
        case_for_empty_first_line.name + ' / must_be_on_current_line=False',
        Arrangement(
            grammar=the_grammar,
            source=case_for_empty_first_line.parse_source,
            must_be_on_current_line=False,
        ),
        Expectation(
            expression=expected_expression,
            source=case_for_empty_first_line.assertion,
        )
    )


def _check_with_must_be_on_current_line_variants(
        put: unittest.TestCase,
        expected_expression: ast.Expr,
        grammars: Sequence[NameAndValue[Grammar]],
        original_source_cases: Sequence[SourceCase],
):
    grammar_cases = [
        NameAndValue(
            the_grammar.name,
            _current_line_case_variants_for_grammar(expected_expression,
                                                    the_grammar.value,
                                                    original_source_cases)
        )
        for the_grammar in grammars
    ]

    for grammar_case in grammar_cases:
        for source_case in grammar_case.value:
            with put.subTest(grammar=grammar_case.name,
                             name=source_case.name):
                _check(
                    put,
                    source_case.arrangement,
                    source_case.expectation,
                )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
