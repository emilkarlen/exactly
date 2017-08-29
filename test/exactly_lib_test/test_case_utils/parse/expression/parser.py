import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.parse.expression import parser as sut
from exactly_lib_test.section_document.test_resources import parse_source as asrt_source
from exactly_lib_test.test_case_utils.parse.expression.test_resources import ast
from exactly_lib_test.test_case_utils.parse.expression.test_resources.ast import ComplexA, ComplexB, PrefixExprP
from exactly_lib_test.test_case_utils.parse.test_resources.source_case import SourceCase
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
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
        if expectation.expression != actual:
            self.fail('Unexpected expression.\nExpected: {}\nActual  : {}'.format(
                str(expectation.expression),
                str(actual),
            ))
        self.assertEqual(expectation.expression,
                         actual,
                         'parsed expression: ' + str(actual))
        expectation.source.apply_with_message(self,
                                              arrangement.source,
                                              'source after parse')


class TestFailuresCommonToAllGrammars(TestCaseBase):
    def test(self):
        grammars = [
            (
                'sans complex expressions',
                ast.GRAMMAR_SANS_COMPLEX_EXPRESSIONS,
            ),
            (
                'with complex expressions',
                ast.GRAMMAR_WITH_ALL_COMPONENTS,
            ),
        ]
        for grammar_description, grammar in grammars:
            cases = [
                (
                    'source is just space',
                    remaining_source('   '),
                ),
                (
                    'first token quoted/soft',
                    remaining_source(str(surrounded_by_soft_quotes('token'))),
                ),
                (
                    'first token quoted/hard',
                    remaining_source(str(surrounded_by_hard_quotes('token'))),
                ),
                (
                    'missing )',
                    remaining_source('( {simple} '.format(simple=ast.SIMPLE_SANS_ARG)),
                ),
                (
                    'missing ), but found on following line',
                    remaining_source('( {simple} '.format(simple=ast.SIMPLE_SANS_ARG),
                                     [')']),
                ),
            ]
            for case_name, source in cases:
                with self.subTest(grammar=grammar_description,
                                  case_name=case_name):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.parse_from_parse_source(grammar,
                                                    source)


class TestSingleSimpleExpression(TestCaseBase):
    grammars = [
        (
            'sans complex expressions',
            ast.GRAMMAR_SANS_COMPLEX_EXPRESSIONS,
        ),
        (
            'with complex expressions',
            ast.GRAMMAR_WITH_ALL_COMPONENTS,
        ),
    ]

    def test_successful_parse_of_expr_sans_argument(self):
        space_after = '           '
        token_after = str(surrounded_by_hard_quotes('not an expression'))
        for grammar_description, grammar in self.grammars:
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
                SourceCase(
                    '( simple )',
                    source=
                    remaining_source('( {simple_expr} )'.format(
                        simple_expr=ast.SIMPLE_SANS_ARG,
                        token_after=token_after)),
                    source_assertion=
                    asrt_source.is_at_end_of_line(1),
                ),
                SourceCase(
                    '( ( simple ) )',
                    source=
                    remaining_source('( ( {simple_expr} ) )'.format(
                        simple_expr=ast.SIMPLE_SANS_ARG,
                        token_after=token_after)),
                    source_assertion=
                    asrt_source.is_at_end_of_line(1),
                ),
            ]

            for case in cases:
                with self.subTest(grammar=grammar_description,
                                  name=case.name):
                    self._check(
                        Arrangement(
                            grammar=grammar,
                            source=case.source),
                        Expectation(
                            expression=ast.SimpleSansArg(),
                            source=case.source_assertion,
                        )
                    )

    def test_successful_parse_of_expr_with_argument(self):
        the_argument = 'the-argument'
        space_after = '           '
        token_after = str(surrounded_by_hard_quotes('not an expression'))
        for grammar_description, grammar in self.grammars:
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
                SourceCase(
                    '( simple )',
                    source=
                    remaining_source('( {simple_with_arg} {argument} )'.format(
                        simple_with_arg=ast.SIMPLE_WITH_ARG,
                        argument=the_argument,
                    )),
                    source_assertion=
                    asrt_source.is_at_end_of_line(1),
                ),
                SourceCase(
                    '( ( simple ) )',
                    source=
                    remaining_source('( ( {simple_with_arg} {argument} ) )'.format(
                        simple_with_arg=ast.SIMPLE_WITH_ARG,
                        argument=the_argument,
                    )),
                    source_assertion=
                    asrt_source.is_at_end_of_line(1),
                ),
            ]
            for case in cases:
                with self.subTest(grammar=grammar_description,
                                  name=case.name):
                    self._check(
                        Arrangement(
                            grammar=grammar,
                            source=case.source),
                        Expectation(
                            expression=ast.SimpleWithArg(the_argument),
                            source=case.source_assertion,
                        )
                    )

    def test_fail(self):
        for grammar_description, grammar in self.grammars:
            cases = [
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
                with self.subTest(grammar=grammar_description,
                                  case_name=case_name):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.parse_from_parse_source(grammar,
                                                    source)


class TestSinglePrefixExpression(TestCaseBase):
    prefix_operators = [
        (
            ast.PREFIX_P,
            ast.PrefixExprP,
        ),
        (
            ast.PREFIX_Q,
            ast.PrefixExprQ,
        ),
    ]

    grammars = [
        (
            'sans complex expressions',
            ast.GRAMMAR_SANS_COMPLEX_EXPRESSIONS,
        ),
        (
            'with complex expressions',
            ast.GRAMMAR_WITH_ALL_COMPONENTS,
        ),
    ]

    def test_successful_parse_with_simple_expr(self):

        space_after = '           '
        token_after = str(surrounded_by_hard_quotes('not an expression'))

        simple_expr = ast.SimpleSansArg()
        simple_expr_src = ast.SIMPLE_SANS_ARG

        for grammar_description, grammar in self.grammars:
            for prefix_operator, mk_prefix_expr in self.prefix_operators:
                cases = [
                    SourceCase(
                        'first line is only simple expr',
                        source=
                        remaining_source('{op} {simple_expr}'.format(
                            op=prefix_operator,
                            simple_expr=simple_expr_src,
                        )),
                        source_assertion=
                        asrt_source.is_at_end_of_line(1)
                    ),
                    SourceCase(
                        'first line is simple expr with space around',
                        source=
                        remaining_source(' {op}  {simple_expr}{space_after}'.format(
                            op=prefix_operator,
                            simple_expr=simple_expr_src,
                            space_after=space_after)),
                        source_assertion=
                        asrt_source.source_is_not_at_end(current_line_number=asrt.equals(1),
                                                         remaining_part_of_current_line=asrt.equals(space_after[1:]))
                    ),
                    SourceCase(
                        'expression is followed by non-expression',
                        source=
                        remaining_source('{op} {simple_expr} {token_after}'.format(
                            op=prefix_operator,
                            simple_expr=simple_expr_src,
                            token_after=token_after)),
                        source_assertion=
                        asrt_source.source_is_not_at_end(current_line_number=asrt.equals(1),
                                                         remaining_part_of_current_line=asrt.equals(token_after))
                    ),
                    SourceCase(
                        '( op simple )',
                        source=
                        remaining_source('( {op} {simple_expr} )'.format(
                            op=prefix_operator,
                            simple_expr=simple_expr_src,
                            token_after=token_after)),
                        source_assertion=
                        asrt_source.is_at_end_of_line(1),
                    ),
                    SourceCase(
                        'op ( simple )',
                        source=
                        remaining_source('{op} ( {simple_expr} )'.format(
                            op=prefix_operator,
                            simple_expr=simple_expr_src,
                            token_after=token_after)),
                        source_assertion=
                        asrt_source.is_at_end_of_line(1),
                    ),
                ]

                for case in cases:
                    with self.subTest(grammar=grammar_description,
                                      prefix_operator=prefix_operator,
                                      name=case.name):
                        self._check(
                            Arrangement(
                                grammar=grammar,
                                source=case.source),
                            Expectation(
                                expression=mk_prefix_expr(simple_expr),
                                source=case.source_assertion,
                            )
                        )

    def test_successful_parse_with_complex_expressions(self):
        s = ast.SimpleSansArg()
        cases = [
            (
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
            (
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
        for case_name, arrangement, expectation in cases:
            with self.subTest(name=case_name):
                self._check(
                    arrangement,
                    expectation
                )

    def test_fail(self):
        for grammar_description, grammar in self.grammars:
            for prefix_operator, mk_prefix_expr in self.prefix_operators:
                cases = [
                    (
                        'no source after operator',
                        remaining_source(prefix_operator),
                    ),
                    (
                        'no source after operator, but expr on following line',
                        remaining_source(prefix_operator,
                                         [ast.SIMPLE_SANS_ARG]),
                    ),
                    (
                        'operator followed by non-expression',
                        remaining_source('{op} {non_expr}'.format(
                            op=prefix_operator,
                            non_expr=str(surrounded_by_soft_quotes(ast.SIMPLE_SANS_ARG)))),
                    ),
                    (
                        'operator followed by expr in ( ), but ) is missing (but one is found on following line)',
                        remaining_source('{op} ( {expr} '.format(
                            op=prefix_operator,
                            expr=ast.SIMPLE_SANS_ARG),
                            [')']),
                    ),
                ]
                for case_name, source in cases:
                    with self.subTest(grammar=grammar_description,
                                      prefix_operator=prefix_operator,
                                      case_name=case_name):
                        with self.assertRaises(SingleInstructionInvalidArgumentException):
                            sut.parse_from_parse_source(grammar,
                                                        source)


class TestSingleRefExpression(TestCaseBase):
    grammars = [
        (
            'sans complex expressions',
            ast.GRAMMAR_SANS_COMPLEX_EXPRESSIONS,
        ),
        (
            'with complex expressions',
            ast.GRAMMAR_WITH_ALL_COMPONENTS,
        ),
    ]

    def test_successful_parse(self):
        symbol_name = 'the_symbol_name'
        space_after = '           '
        token_after = str(surrounded_by_hard_quotes('not an expression'))
        for grammar_description, grammar in self.grammars:
            cases = [
                SourceCase(
                    'first line is only simple expr',
                    source=
                    remaining_source('{symbol_name}'.format(
                        symbol_name=symbol_name,
                    )),
                    source_assertion=
                    asrt_source.is_at_end_of_line(1)
                ),
                SourceCase(
                    'first line is simple expr with space around',
                    source=
                    remaining_source('  {symbol_name}{space_after}'.format(
                        symbol_name=symbol_name,
                        space_after=space_after)),
                    source_assertion=
                    asrt_source.source_is_not_at_end(current_line_number=asrt.equals(1),
                                                     remaining_part_of_current_line=asrt.equals(space_after[1:]))
                ),
                SourceCase(
                    'expression is followed by non-expression',
                    source=
                    remaining_source('{symbol_name} {token_after}'.format(
                        symbol_name=symbol_name,
                        token_after=token_after)),
                    source_assertion=
                    asrt_source.source_is_not_at_end(current_line_number=asrt.equals(1),
                                                     remaining_part_of_current_line=asrt.equals(token_after))
                ),
            ]

            for case in cases:
                with self.subTest(grammar=grammar_description,
                                  name=case.name):
                    self._check(
                        Arrangement(
                            grammar=grammar,
                            source=case.source),
                        Expectation(
                            expression=ast.RefExpr(symbol_name),
                            source=case.source_assertion,
                        )
                    )

    def test_fail(self):
        symbol_name = 'the_symbol_name'
        for grammar_description, grammar in self.grammars:
            cases = [
                (
                    'symbol name is quoted',
                    remaining_source(str(surrounded_by_hard_quotes(symbol_name))),
                ),
            ]
            for case_name, source in cases:
                with self.subTest(grammar=grammar_description,
                                  case_name=case_name):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.parse_from_parse_source(grammar,
                                                    source)


class TestComplexExpression(TestCaseBase):
    def test_success_of_single_operator(self):
        space_after = '           '
        quoted_string = str(surrounded_by_hard_quotes('quoted string'))

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

        for valid_simple_expr_source, expected_simple_expr in valid_simple_expressions:
            for operator_source, operator_constructor in operators:
                expected_expression = operator_constructor([expected_simple_expr,
                                                            expected_simple_expr])
                cases = [
                    SourceCase(
                        'first line is just complex expr',
                        source=
                        remaining_source('{simple_expr} {operator} {simple_expr}'.format(
                            simple_expr=valid_simple_expr_source,
                            operator=operator_source,
                        )),
                        source_assertion=
                        asrt_source.is_at_end_of_line(1)
                    ),
                    SourceCase(
                        'first line is complex expr, followed by space',
                        source=
                        remaining_source('{simple_expr} {operator} {simple_expr}{space_after}'.format(
                            simple_expr=valid_simple_expr_source,
                            operator=operator_source,
                            space_after=space_after,
                        )),
                        source_assertion=
                        asrt_source.source_is_not_at_end(
                            current_line_number=asrt.equals(1),
                            remaining_part_of_current_line=asrt.equals(space_after[1:]))
                    ),
                    SourceCase(
                        'complex expr followed by non-operator',
                        source=
                        remaining_source('{simple_expr} {operator} {simple_expr} {quoted_string}'.format(
                            simple_expr=valid_simple_expr_source,
                            operator=operator_source,
                            quoted_string=quoted_string,
                        )),
                        source_assertion=
                        asrt_source.source_is_not_at_end(
                            current_line_number=asrt.equals(1),
                            remaining_part_of_current_line=asrt.equals(quoted_string))

                    ),
                    SourceCase(
                        'complex expr followed by simple expression',
                        source=
                        remaining_source('{simple_expr} {operator} {simple_expr} {simple_expr}'.format(
                            simple_expr=valid_simple_expr_source,
                            operator=operator_source,
                        )),
                        source_assertion=
                        asrt_source.source_is_not_at_end(
                            current_line_number=asrt.equals(1),
                            remaining_part_of_current_line=asrt.equals(valid_simple_expr_source))

                    ),
                    SourceCase(
                        'complex expr followed by quoted operator',
                        source=
                        remaining_source('{simple_expr} {operator} {simple_expr} {quoted_operator}'.format(
                            simple_expr=valid_simple_expr_source,
                            operator=operator_source,
                            quoted_operator=surrounded_by_soft_quotes(operator_source),
                        )),
                        source_assertion=
                        asrt_source.source_is_not_at_end(
                            current_line_number=asrt.equals(1),
                            remaining_part_of_current_line=asrt.equals(str(surrounded_by_soft_quotes(operator_source))))

                    ),
                    SourceCase(
                        'first line is just complex expr: inside ()',
                        source=
                        remaining_source('( {simple_expr} {operator} {simple_expr} )'.format(
                            simple_expr=valid_simple_expr_source,
                            operator=operator_source,
                        )),
                        source_assertion=
                        asrt_source.is_at_end_of_line(1)
                    ),
                    SourceCase(
                        'first simple expr inside ()',
                        source=
                        remaining_source('( {simple_expr} ) {operator} {simple_expr}'.format(
                            simple_expr=valid_simple_expr_source,
                            operator=operator_source,
                        )),
                        source_assertion=
                        asrt_source.is_at_end_of_line(1)
                    ),
                    SourceCase(
                        'second simple expr inside ()',
                        source=
                        remaining_source('{simple_expr} {operator} ( {simple_expr} )'.format(
                            simple_expr=valid_simple_expr_source,
                            operator=operator_source,
                        )),
                        source_assertion=
                        asrt_source.is_at_end_of_line(1)
                    ),
                ]
                for case in cases:
                    with self.subTest(name=case.name,
                                      operator_source=operator_source,
                                      valid_simple_expr_source=valid_simple_expr_source):
                        self._check(
                            Arrangement(
                                grammar=
                                ast.GRAMMAR_WITH_ALL_COMPONENTS,
                                source=
                                case.source),
                            Expectation(
                                expression=
                                expected_expression,
                                source=
                                case.source_assertion,
                            )
                        )

    def test_success_of_expression_within_parentheses(self):
        s = ast.SimpleSansArg()
        cases = [
            (
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
            (
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
            (
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
        ]
        for case_name, arrangement, expectation in cases:
            with self.subTest(name=case_name):
                self._check(
                    arrangement,
                    expectation
                )

    def test_fail_parse_of_complex_expression(self):
        valid_simple_expressions = [
            '{simple_expression}'.format(simple_expression=ast.SIMPLE_SANS_ARG),
            '{simple_expression_name} {argument}'.format(
                simple_expression_name=ast.SIMPLE_WITH_ARG,
                argument='simple-expr-argument'),

        ]
        operators = [ast.COMPLEX_A,
                     ast.COMPLEX_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME]

        for valid_simple_expr in valid_simple_expressions:
            for operator in operators:
                cases = [
                    (
                        'operator not followed by expression',
                        remaining_source('{simple_expr} {operator}'.format(
                            simple_expr=valid_simple_expr,
                            operator=operator,
                        )),
                    ),
                    (
                        'operator followed by non-expression',
                        remaining_source('{simple_expr} {operator} {non_expr}'.format(
                            simple_expr=valid_simple_expr,
                            operator=operator,
                            non_expr=ast.NOT_A_SIMPLE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME,
                        )),
                    ),
                    (
                        'operator followed by non-expression/two operators',
                        remaining_source('{simple_expr} {operator} {simple_expr} {operator} {non_expr}'.format(
                            simple_expr=valid_simple_expr,
                            operator=operator,
                            non_expr=ast.NOT_A_SIMPLE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME,
                        )),
                    ),
                    (
                        'operator followed by expression, but following expression is on next line',
                        remaining_source('{simple_expr} {operator} '.format(
                            simple_expr=valid_simple_expr,
                            operator=operator),
                            [valid_simple_expr]),
                    ),
                    (
                        'operator followed by expression, but following expression is on next line/two operators',
                        remaining_source('{simple_expr} {operator} {simple_expr} {operator} '.format(
                            simple_expr=valid_simple_expr,
                            operator=operator),
                            [valid_simple_expr]),
                    ),
                    (
                        '( at start of expr: missing )',
                        remaining_source('( {simple_expr} {operator} {simple_expr} '.format(
                            simple_expr=valid_simple_expr,
                            operator=operator),
                            []),
                    ),
                    (
                        '( at start of expr: missing ), but found on following line',
                        remaining_source('( {simple_expr} {operator} {simple_expr} '.format(
                            simple_expr=valid_simple_expr,
                            operator=operator),
                            [')']),
                    ),
                    (
                        '( in middle of expr: missing )',
                        remaining_source('( {simple_expr} {operator} ( {simple_expr} '.format(
                            simple_expr=valid_simple_expr,
                            operator=operator),
                            []),
                    ),
                    (
                        '( in middle of expr: missing ), but found on following line',
                        remaining_source(' {simple_expr} {operator} ( {simple_expr} '.format(
                            simple_expr=valid_simple_expr,
                            operator=operator),
                            [')']),
                    ),
                ]
                for case_name, source in cases:
                    with self.subTest(case_name=case_name,
                                      operator=operator,
                                      valid_simple_expr=valid_simple_expr):
                        with self.assertRaises(SingleInstructionInvalidArgumentException):
                            sut.parse_from_parse_source(ast.GRAMMAR_WITH_ALL_COMPONENTS,
                                                        source)


class TestCombinedExpressions(TestCaseBase):
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


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
