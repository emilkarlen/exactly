import unittest
from typing import List

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.str_.formatter import StringFormatter
from exactly_lib_test.impls.types.expression.test_resources import parse_w_variants_cases, parse_check, \
    test_grammars
from exactly_lib_test.impls.types.expression.test_resources import test_grammars as ast
from exactly_lib_test.impls.types.expression.test_resources.case_generation import \
    current_line_case_variants_for_grammar
from exactly_lib_test.impls.types.expression.test_resources.ex_arr import Arrangement, Expectation, \
    SourceExpectation, SourceCase
from exactly_lib_test.impls.types.expression.test_resources.parse_check import check, \
    PARSER_MAKER_OF_FULL_EXPR_PARSER
from exactly_lib_test.impls.types.expression.test_resources.test_grammars import InfixOpA, InfixOpB, PrefixOpExprP
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source, source_of_lines, \
    remaining_source_string
from exactly_lib_test.test_resources.test_utils import NArrEx
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.quoting import surrounded_by_soft_quotes, surrounded_by_hard_quotes


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([

        unittest.makeSuite(TestFailuresCommonToAllGrammarsForSimpleExprParser),
        unittest.makeSuite(TestSinglePrimitiveExpressionForSimpleExprParser),
        unittest.makeSuite(TestSinglePrefixOpExpressionForSimpleExprParser),
        unittest.makeSuite(TestSingleRefExpressionForSimpleExprParser),

        unittest.makeSuite(TestFailuresCommonToAllGrammarsForFullExprParser),
        unittest.makeSuite(TestSinglePrimitiveExpressionForFullExprParser),
        unittest.makeSuite(TestSinglePrefixOpExpressionForFullExprParser),
        unittest.makeSuite(TestSingleRefExpressionForFullExprParser),

        unittest.makeSuite(TestSpecificForSimpleExprParse),

        unittest.makeSuite(TestInfixOpExpression),
        unittest.makeSuite(TestCombinedExpressions),
    ])


class TestFailuresCommonToAllGrammarsForSimpleExprParser(parse_w_variants_cases.WithParserMakerOfSimpleExprParser,
                                                         parse_w_variants_cases.TestFailuresCommonToAllGrammars):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestSinglePrimitiveExpressionForSimpleExprParser(parse_w_variants_cases.WithParserMakerOfSimpleExprParser,
                                                       parse_w_variants_cases.TestSinglePrimitiveExpression):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestSinglePrefixOpExpressionForSimpleExprParser(parse_w_variants_cases.WithParserMakerOfSimpleExprParser,
                                                      parse_w_variants_cases.TestSinglePrefixOpExpression):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestSingleRefExpressionForSimpleExprParser(parse_w_variants_cases.WithParserMakerOfSimpleExprParser,
                                                 parse_w_variants_cases.TestSingleRefExpression):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestFailuresCommonToAllGrammarsForFullExprParser(parse_w_variants_cases.WithParserMakerOfFullExprParser,
                                                       parse_w_variants_cases.TestFailuresCommonToAllGrammars):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestSinglePrimitiveExpressionForFullExprParser(parse_w_variants_cases.WithParserMakerOfFullExprParser,
                                                     parse_w_variants_cases.TestSinglePrimitiveExpression):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestSinglePrefixOpExpressionForFullExprParser(parse_w_variants_cases.WithParserMakerOfFullExprParser,
                                                    parse_w_variants_cases.TestSinglePrefixOpExpression):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestSingleRefExpressionForFullExprParser(parse_w_variants_cases.WithParserMakerOfFullExprParser,
                                               parse_w_variants_cases.TestSingleRefExpression):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    pass


class TestSpecificForSimpleExprParse(unittest.TestCase):
    def test_successful_parse_of_expr_sans_argument(self):
        infix_op_and_expr_after = ' '.join([ast.INFIX_OP_A, ast.PRIMITIVE_SANS_ARG])

        format_map = {
            'primitive_expr': ast.PRIMITIVE_SANS_ARG,
            'infix_op_and_expr_after': infix_op_and_expr_after,
        }

        def source(s: str) -> str:
            return s.format_map(format_map)

        cases = [
            SourceCase(
                'primitive followed by INFIX-OP EXPR',
                source('{primitive_expr} {infix_op_and_expr_after}'),
                SourceExpectation.source_is_not_at_end(current_line_number=1,
                                                       remaining_part_of_current_line=infix_op_and_expr_after),
            ),
            SourceCase(
                '( primitive ) followed by INFIX-OP EXPR',
                source('( {primitive_expr} ) {infix_op_and_expr_after}'),
                SourceExpectation.source_is_not_at_end(current_line_number=1,
                                                       remaining_part_of_current_line=infix_op_and_expr_after),
            ),
        ]
        # ACT & ASSERT #
        parse_check.check_with_must_be_on_current_line_variants(
            self,
            parse_check.PARSER_MAKER_OF_SIMPLE_EXPR_PARSER,
            ast.PrimitiveSansArg(),
            test_grammars.GRAMMARS,
            cases,
        )

    def test_successful_parse_of_expr_with_argument(self):
        # ARRANGE #

        the_argument = 'the-argument'
        infix_op_and_expr_after = ' '.join([ast.INFIX_OP_A, ast.PRIMITIVE_SANS_ARG])

        format_map = {
            'primitive_with_arg': ast.PRIMITIVE_WITH_ARG,
            'argument': the_argument,
            'infix_op_and_expr_after': infix_op_and_expr_after,
        }

        def source(s: str) -> str:
            return s.format_map(format_map)

        cases = [
            SourceCase(
                'primitive_with_arg INFIX-OP EXPR',
                source('{primitive_with_arg} {argument} {infix_op_and_expr_after}'),
                SourceExpectation.source_is_not_at_end(current_line_number=1,
                                                       remaining_part_of_current_line=infix_op_and_expr_after),
            ),
            SourceCase(
                '( primitive_with_arg ) INFIX-OP EXPR',
                source('( {primitive_with_arg} {argument} ) {infix_op_and_expr_after}'),
                SourceExpectation.source_is_not_at_end(current_line_number=1,
                                                       remaining_part_of_current_line=infix_op_and_expr_after),
            ),
        ]

        # ACT & ASSERT #

        parse_check.check_with_must_be_on_current_line_variants(
            self,
            parse_check.PARSER_MAKER_OF_SIMPLE_EXPR_PARSER,
            ast.PrimitiveWithArg(the_argument),
            test_grammars.GRAMMARS,
            cases,
        )


class TestInfixOpExpression(unittest.TestCase):
    def test_success_of_single_operator(self):
        valid_primitive_expressions = [
            (
                '{primitive_expression}'.format(primitive_expression=ast.PRIMITIVE_SANS_ARG),
                ast.PrimitiveSansArg()
            ),
            (
                '{primitive_expression_name} {argument}'.format(
                    primitive_expression_name=ast.PRIMITIVE_WITH_ARG,
                    argument='primitive-expr-argument'),
                ast.PrimitiveWithArg('primitive-expr-argument')
            ),

        ]
        operators = [
            (
                ast.INFIX_OP_A,
                ast.InfixOpA,
            ),
            (
                ast.INFIX_OP_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME,
                ast.InfixOpB,
            ),
        ]

        def source_cases_for_expressions(primitive_expr: str,
                                         operator: str) -> List[SourceCase]:
            sf = StringFormatter({
                'primitive_expr': primitive_expr,
                'operator': operator,
                'quoted_operator': surrounded_by_soft_quotes(operator_source),
                'space_after': '           ',
                'quoted_string': surrounded_by_hard_quotes('quoted string'),

            })

            def source(template: str) -> str:
                return sf.format(template)

            return [
                SourceCase(
                    'first line is just infix op expr',
                    source('{primitive_expr} {operator} {primitive_expr}'),
                    SourceExpectation.is_at_end_of_line(1)
                ),
                SourceCase(
                    'first line is infix op expr, followed by space',
                    source('{primitive_expr} {operator} {primitive_expr}{space_after}'),
                    SourceExpectation.source_is_not_at_end(
                        current_line_number=1,
                        remaining_part_of_current_line=sf.format('{space_after}')[1:])
                ),
                SourceCase(
                    'infix op expr followed by non-operator',
                    source('{primitive_expr} {operator} {primitive_expr} {quoted_string}'),
                    SourceExpectation.source_is_not_at_end(
                        current_line_number=1,
                        remaining_part_of_current_line=sf.format('{quoted_string}'))
                ),
                SourceCase(
                    'infix op expr followed by primitive expression',
                    source('{primitive_expr} {operator} {primitive_expr} {primitive_expr}'),
                    SourceExpectation.source_is_not_at_end(
                        current_line_number=1,
                        remaining_part_of_current_line=sf.format('{primitive_expr}'))
                ),
                SourceCase(
                    'infix op expr followed by quoted operator',
                    source('{primitive_expr} {operator} {primitive_expr} {quoted_operator}'),
                    SourceExpectation.source_is_not_at_end(
                        current_line_number=1,
                        remaining_part_of_current_line=sf.format('{quoted_operator}'))
                ),
                SourceCase(
                    'first line is just infix op expr: inside ()',
                    source('( {primitive_expr} {operator} {primitive_expr} )'),
                    SourceExpectation.is_at_end_of_line(1)
                ),
                SourceCase(
                    'first primitive expr inside ()',
                    source('( {primitive_expr} ) {operator} {primitive_expr}'),
                    SourceExpectation.is_at_end_of_line(1)
                ),
                SourceCase(
                    'second primitive expr inside ()',
                    source('{primitive_expr} {operator} ( {primitive_expr} )'),
                    SourceExpectation.is_at_end_of_line(1)
                ),
                SourceCase(
                    'second expr on following line',
                    source('{primitive_expr} {operator}\n{primitive_expr}'),
                    SourceExpectation.is_at_end_of_line(2)
                ),
            ]

        for valid_primitive_expr_source, expected_primitive_expr in valid_primitive_expressions:
            for operator_source, operator_constructor in operators:
                expected_expression = operator_constructor([expected_primitive_expr,
                                                            expected_primitive_expr])
                source_cases = source_cases_for_expressions(valid_primitive_expr_source, operator_source)
                cases = current_line_case_variants_for_grammar(expected_expression,
                                                               ast.GRAMMAR_WITH_ALL_COMPONENTS,
                                                               source_cases)

                for case in cases:
                    with self.subTest(name=case.name,
                                      operator_source=operator_source,
                                      valid_primitive_expr_source=valid_primitive_expr_source):
                        check(self,
                              PARSER_MAKER_OF_FULL_EXPR_PARSER,
                              case.arrangement,
                              case.expectation)

    def test_successful_parse_with_infix_op_expressions(self):
        s = ast.PrimitiveSansArg()
        cases = [
            NArrEx(
                'prefix operator binds to following primitive expression (single infix ops)',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('{p_op} {s}  {bin_op}  {s}  {bin_op}  {p_op} {s}'.format(
                        s=ast.PRIMITIVE_SANS_ARG,
                        p_op=ast.PREFIX_P,
                        bin_op=ast.INFIX_OP_A,
                    )),
                ),
                Expectation(
                    expression=InfixOpA([PrefixOpExprP(s), s, PrefixOpExprP(s)]),
                    source=asrt_source.is_at_end_of_line(1),
                ),
            ),
            NArrEx(
                'prefix operator binds to following primitive expression (different infix ops)',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('{p_op} {s}  {bin_op_a}  {s}  {bin_op_b}  {p_op} {s}'.format(
                        s=ast.PRIMITIVE_SANS_ARG,
                        p_op=ast.PREFIX_P,
                        bin_op_a=ast.INFIX_OP_A,
                        bin_op_b=ast.INFIX_OP_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME,
                    )),
                ),
                Expectation(
                    expression=InfixOpB([InfixOpA([PrefixOpExprP(s), s]), PrefixOpExprP(s)]),
                    source=asrt_source.is_at_end_of_line(1),
                ),
            ),
        ]
        # ACT & ASSERT #

        parse_check.check__multi(self, PARSER_MAKER_OF_FULL_EXPR_PARSER, cases)

    def test_success_of_expression_within_parentheses(self):
        s = ast.PrimitiveSansArg()
        cases = [
            NArrEx(
                'parentheses around first expr to make nested expr instead of "linear" args to op',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('( {s} {op}  {s} ) {op} {s}'.format(
                        s=ast.PRIMITIVE_SANS_ARG,
                        op=ast.INFIX_OP_A,
                    )),
                ),
                Expectation(
                    expression=InfixOpA([InfixOpA([s, s]), s]),
                    source=asrt_source.is_at_end_of_line(1),
                ),
            ),
            NArrEx(
                'parentheses around final (second) expr to make first op have precedence',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('{s} {op} ( {s} {op} {s} )'.format(
                        s=ast.PRIMITIVE_SANS_ARG,
                        op=ast.INFIX_OP_A,
                    )),
                ),
                Expectation(
                    expression=InfixOpA([s, InfixOpA([s, s])]),
                    source=asrt_source.is_at_end_of_line(1),
                ),
            ),
            NArrEx(
                '"linear" (sequence) of OPA, by embedding OPB inside parentheses',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('{s} {op_a} ( {s} {op_b} {s} ) {op_a} {s}'.format(
                        s=ast.PRIMITIVE_SANS_ARG,
                        op_a=ast.INFIX_OP_A,
                        op_b=ast.INFIX_OP_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME,
                    )),
                ),
                Expectation(
                    expression=InfixOpA([s, InfixOpB([s, s]), s]),
                    source=asrt_source.is_at_end_of_line(1),
                ),
            ),
            NArrEx(
                'parentheses around expr should allow binary operator to be on separate lines',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=source_of_lines([
                        '(',
                        ast.PRIMITIVE_SANS_ARG,
                        ast.INFIX_OP_A,
                        ast.PRIMITIVE_SANS_ARG,
                        ')',
                    ]),
                ),
                Expectation(
                    expression=InfixOpA([s, s]),
                    source=asrt_source.is_at_end_of_line(5),
                ),
            ),

        ]
        for case in cases:
            with self.subTest(name=case.name):
                check(self,
                      PARSER_MAKER_OF_FULL_EXPR_PARSER,
                      case.arrangement,
                      case.expectation
                      )

    def test_success_of_expression_within_parentheses_spanning_several_lines(self):
        s = ast.PrimitiveSansArg()
        cases = [
            NArrEx(
                'primitive expr and ) on following line',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('(',
                                            ['{s} )'.format(s=ast.PRIMITIVE_SANS_ARG)]),
                ),
                Expectation(
                    expression=s,
                    source=asrt_source.is_at_end_of_line(2),
                ),
            ),
            NArrEx(
                'primitive expr and ) on following line, followed by non-expr',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('(',
                                            ['{s} ) non-expr'.format(s=ast.PRIMITIVE_SANS_ARG)]),
                ),
                Expectation(
                    expression=s,
                    source=asrt_source.source_is_not_at_end(current_line_number=asrt.equals(2),
                                                            remaining_part_of_current_line=asrt.equals('non-expr')),
                ),
            ),
            NArrEx(
                'primitive expr with ) on following line',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('( {s}'.format(s=ast.PRIMITIVE_SANS_ARG),
                                            [' )']),
                ),
                Expectation(
                    expression=s,
                    source=asrt_source.is_at_end_of_line(2),
                ),
            ),
            NArrEx(
                'primitive expr with ) on following line, and non-expr on line after that',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('( {s}'.format(s=ast.PRIMITIVE_SANS_ARG),
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
                                            [' {s} {op} {s} )'.format(s=ast.PRIMITIVE_SANS_ARG,
                                                                      op=ast.INFIX_OP_A)
                                             ]),
                ),
                Expectation(
                    expression=InfixOpA([s, s]),
                    source=asrt_source.is_at_end_of_line(2),
                ),
            ),
            NArrEx(
                'binary op with ) on following line',
                Arrangement(
                    grammar=ast.GRAMMAR_WITH_ALL_COMPONENTS,
                    source=remaining_source('( {s} {op} {s}'.format(s=ast.PRIMITIVE_SANS_ARG,
                                                                    op=ast.INFIX_OP_A),
                                            [' ) ']),
                ),
                Expectation(
                    expression=InfixOpA([s, s]),
                    source=asrt_source.is_at_end_of_line(2),
                ),
            ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                check(self,
                      PARSER_MAKER_OF_FULL_EXPR_PARSER,
                      case.arrangement,
                      case.expectation
                      )

    def test_fail_parse_of_infix_op_expression(self):
        # ARRANGE #
        valid_primitive_expressions = [
            '{primitive_expression}'.format(primitive_expression=ast.PRIMITIVE_SANS_ARG),
            '{primitive_expression_name} {argument}'.format(
                primitive_expression_name=ast.PRIMITIVE_WITH_ARG,
                argument='primitive-expr-argument'),

        ]
        operators = [ast.INFIX_OP_A,
                     ast.INFIX_OP_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME]

        def cases_for(primitive_expr: str, the_operator: str) -> List[NameAndValue[str]]:
            sf = StringFormatter({
                'primitive_expr': primitive_expr,
                'operator': the_operator,
                'non_expr': ast.NOT_A_PRIMITIVE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME,

            })

            return [
                NameAndValue(
                    'operator not followed by expression',
                    sf.format('{primitive_expr} {operator}'),
                ),
                NameAndValue(
                    'operator followed by non-expression',
                    sf.format('{primitive_expr} {operator} {non_expr}'),
                ),
                NameAndValue(
                    'operator followed by non-expression/two operators',
                    sf.format('{primitive_expr} {operator} {primitive_expr} {operator} {non_expr}'),
                ),
                NameAndValue(
                    '( at start of expr: missing )',
                    sf.format('( {primitive_expr} {operator} {primitive_expr} '),
                ),
                NameAndValue(
                    '( in middle of expr: missing )',
                    sf.format('( {primitive_expr} {operator} ( {primitive_expr} '),
                ),
            ]

        for valid_primitive_expr in valid_primitive_expressions:
            for operator in operators:
                cases = cases_for(valid_primitive_expr, operator)
                # With source on first line
                for must_be_on_current_line in [False, True]:
                    for case in cases:
                        with self.subTest(case_name=case.name,
                                          operator=operator,
                                          valid_primitive_expr=valid_primitive_expr,
                                          source='appears on first line',
                                          must_be_on_current_line=must_be_on_current_line):
                            # ACT & ASSERT #
                            parser = PARSER_MAKER_OF_FULL_EXPR_PARSER.make(
                                ast.GRAMMAR_WITH_ALL_COMPONENTS,
                                must_be_on_current_line=must_be_on_current_line,
                            )
                            with self.assertRaises(SingleInstructionInvalidArgumentException):
                                parser.parse(remaining_source_string(case.value))

                # With source not on first line
                for case in cases:
                    with self.subTest(case_name=case.name,
                                      operator=operator,
                                      valid_primitive_expr=valid_primitive_expr,
                                      source='appears not on first line',
                                      must_be_on_current_line=must_be_on_current_line):
                        parse_source = remaining_source_string('\n' + case.value)
                        parser = PARSER_MAKER_OF_FULL_EXPR_PARSER.make(ast.GRAMMAR_WITH_ALL_COMPONENTS,
                                                                       must_be_on_current_line=False)
                        # ACT & ASSERT #
                        with self.assertRaises(SingleInstructionInvalidArgumentException):
                            parser.parse(parse_source)


class TestCombinedExpressions(unittest.TestCase):
    def test__inside_parentheses__primitive_recursive_followed_by_binary_op(self):
        s = ast.PrimitiveSansArg()

        expected = ast.InfixOpA([ast.PrimitiveRecursive(s), s])

        cases = [
            NameAndValue(
                'bin op on same line',
                '( \n {r} {s} \n {op_a} \n {s} \n )'.format(
                    r=ast.PRIMITIVE_RECURSIVE,
                    s=ast.PRIMITIVE_SANS_ARG,
                    op_a=ast.INFIX_OP_A,
                ),
            ),
            NameAndValue(
                'bin op on following line',
                '( \n {r} {s} {op_a} \n {s} \n )'.format(
                    r=ast.PRIMITIVE_RECURSIVE,
                    s=ast.PRIMITIVE_SANS_ARG,
                    op_a=ast.INFIX_OP_A,
                ),
            ),
        ]
        for case in cases:
            expected_source = asrt_source.is_at_end_of_line(len(case.value.splitlines()))
            with self.subTest(case.name):
                check(
                    self,
                    PARSER_MAKER_OF_FULL_EXPR_PARSER,
                    Arrangement(
                        grammar=
                        ast.GRAMMAR_WITH_ALL_COMPONENTS,
                        source=
                        remaining_source(case.value)),
                    Expectation(
                        expression=
                        expected,
                        source=
                        expected_source,
                    )
                )

    def test__primitive_recursive_followed_by_binary_op_on_same_line(self):
        s = ast.PrimitiveSansArg()

        expected = ast.InfixOpA([ast.PrimitiveRecursive(s), s])

        arguments = '{r} {s} {op_a} {s}'.format(
            r=ast.PRIMITIVE_RECURSIVE,
            s=ast.PRIMITIVE_SANS_ARG,
            op_a=ast.INFIX_OP_A,
        )

        check(
            self,
            PARSER_MAKER_OF_FULL_EXPR_PARSER,
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

    def test_combined_expression_with_single_primitive_expr(self):
        # [ [ [ s A s ] B s B  s ] A s ]

        s = ast.PrimitiveSansArg()

        op_sequence_1 = ast.InfixOpA([s, s])
        op_sequence_2 = ast.InfixOpB([op_sequence_1, s, s])
        expected = ast.InfixOpA([op_sequence_2, s])

        arguments = '{s} {op_a} {s} {op_b} {s} {op_b} {s} {op_a} {s}'.format(
            op_a=ast.INFIX_OP_A,
            op_b=ast.INFIX_OP_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME,
            s=ast.PRIMITIVE_SANS_ARG,
        )

        check(
            self,
            PARSER_MAKER_OF_FULL_EXPR_PARSER,
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

        s = ast.PrimitiveSansArg()

        s_x = ast.PrimitiveWithArg('X')

        e1 = ast.InfixOpA([
            ref_1,
            s,
        ])
        e2 = ast.InfixOpB([
            e1,
            s,
            ref_2,
        ])
        expected = ast.InfixOpA([
            e2,
            s_x,
            ref_3,
        ])

        argument_string = '{ref_1} {op_a} {s} {op_b} {s} {op_b} {ref_2} {op_a} {s_w_arg} {x} {op_a} {ref_3}'.format(
            s=ast.PRIMITIVE_SANS_ARG,
            ref_1=ref_1.symbol_name,
            ref_2=ref_2.symbol_name,
            ref_3=ref_3.symbol_name,
            op_a=ast.INFIX_OP_A,
            op_b=ast.INFIX_OP_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME,
            s_w_arg=ast.PRIMITIVE_WITH_ARG,
            x=s_x.argument,

        )
        check(
            self,
            PARSER_MAKER_OF_FULL_EXPR_PARSER,
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

        s = ast.PrimitiveSansArg()

        s_x = ast.PrimitiveWithArg('X')
        s_y = ast.PrimitiveWithArg('Y')

        expected = InfixOpB([
            InfixOpA([
                ref_1,
                InfixOpB([s, s_x, ref_2])
            ]),
            s_y,
        ])

        argument_string = '{ref_1} {op_a} ( {s} {op_b} {s_w_arg} {x} {op_b} {ref_2} ) {op_b} {s_w_arg} {y}'.format(
            s=ast.PRIMITIVE_SANS_ARG,
            ref_1=ref_1.symbol_name,
            ref_2=ref_2.symbol_name,
            ref_3=ref_3.symbol_name,
            op_a=ast.INFIX_OP_A,
            op_b=ast.INFIX_OP_B_THAT_IS_NOT_A_VALID_SYMBOL_NAME,
            s_w_arg=ast.PRIMITIVE_WITH_ARG,
            x=s_x.argument,
            y=s_y.argument,

        )
        check(
            self,
            PARSER_MAKER_OF_FULL_EXPR_PARSER,
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
