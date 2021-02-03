import itertools
import unittest
from abc import ABC, abstractmethod
from typing import List

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.str_.formatter import StringFormatter
from exactly_lib_test.impls.types.expression.test_resources import parse_check
from exactly_lib_test.impls.types.expression.test_resources import test_grammars as ast
from exactly_lib_test.impls.types.expression.test_resources.case_generation import \
    current_line_case_variants_for_grammar
from exactly_lib_test.impls.types.expression.test_resources.ex_arr import SourceCase, SourceExpectation, \
    Arrangement, Expectation
from exactly_lib_test.impls.types.expression.test_resources.parse_check import ParserMaker
from exactly_lib_test.impls.types.expression.test_resources.test_grammars import GRAMMARS
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.util.test_resources.quoting import surrounded_by_soft_quotes, surrounded_by_hard_quotes


class WithParserMaker(ABC):
    @property
    @abstractmethod
    def parser_maker(self) -> ParserMaker:
        pass


class _TextCaseWithParserVariantsBase(WithParserMaker, unittest.TestCase, ABC):
    pass


class WithParserMakerOfFullExprParser(WithParserMaker):
    @property
    def parser_maker(self) -> ParserMaker:
        return parse_check.PARSER_MAKER_OF_FULL_EXPR_PARSER


class WithParserMakerOfSimpleExprParser(WithParserMaker):
    @property
    def parser_maker(self) -> ParserMaker:
        return parse_check.PARSER_MAKER_OF_SIMPLE_EXPR_PARSER


class TestFailuresCommonToAllGrammars(_TextCaseWithParserVariantsBase, ABC):
    def test(self):
        for must_be_on_current_line in [False, True]:
            for grammar in GRAMMARS:
                parser = self.parser_maker.make(grammar.value, must_be_on_current_line)
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
                        remaining_source('( {primitive} '.format(primitive=ast.PRIMITIVE_SANS_ARG)),
                    ),
                ]
                for case in cases:
                    with self.subTest(grammar=grammar.name,
                                      must_be_on_current_line=must_be_on_current_line,
                                      case_name=case.name):
                        with self.assertRaises(SingleInstructionInvalidArgumentException):
                            parser.parse(case.value)


class TestSinglePrimitiveExpression(_TextCaseWithParserVariantsBase, ABC):
    def test_successful_parse_of_expr_sans_argument(self):
        space_after = '           '
        token_after = str(surrounded_by_hard_quotes('not an expression'))

        format_map = {
            'primitive_expr': ast.PRIMITIVE_SANS_ARG,
            'space_after': space_after,
            'token_after': token_after,
        }

        def source(s: str) -> str:
            return s.format_map(format_map)

        cases = [
            SourceCase(
                'first line is only primitive expr',
                source('{primitive_expr}'),
                SourceExpectation.is_at_end_of_line(1)
            ),
            SourceCase(
                'first line is primitive expr with space around',
                source('  {primitive_expr}{space_after}'),
                SourceExpectation.source_is_not_at_end(current_line_number=1,
                                                       remaining_part_of_current_line=space_after[1:])
            ),
            SourceCase(
                'expression is followed by non-expression',
                source('{primitive_expr} {token_after}'),
                SourceExpectation.source_is_not_at_end(current_line_number=1,
                                                       remaining_part_of_current_line=token_after)
            ),
            SourceCase(
                '( primitive )',
                source('( {primitive_expr} )'),
                SourceExpectation.is_at_end_of_line(1),
            ),
            SourceCase(
                '( primitive ) followed by non-expression',
                source('( {primitive_expr} ) {token_after}'),
                SourceExpectation.source_is_not_at_end(current_line_number=1,
                                                       remaining_part_of_current_line=token_after),
            ),
            SourceCase(
                '( ( primitive ) )',
                source('( ( {primitive_expr} ) )'),
                SourceExpectation.is_at_end_of_line(1),
            ),
        ]
        # ACT & ASSERT #
        parse_check.check_with_must_be_on_current_line_variants(
            self,
            self.parser_maker,
            ast.PrimitiveSansArg(),
            GRAMMARS,
            cases,
        )

    def test_successful_parse_of_expr_with_argument(self):
        # ARRANGE #

        the_argument = 'the-argument'
        space_after = '           '
        token_after = str(surrounded_by_hard_quotes('not an expression'))

        format_map = {
            'primitive_with_arg': ast.PRIMITIVE_WITH_ARG,
            'argument': the_argument,
            'space_after': space_after,
            'token_after': token_after,
        }

        def source(s: str) -> str:
            return s.format_map(format_map)

        cases = [
            SourceCase(
                'first line is only primitive expr',
                source('{primitive_with_arg} {argument}'),
                SourceExpectation.is_at_end_of_line(1)
            ),
            SourceCase(
                'first line is primitive expr with space around',
                source('  {primitive_with_arg}    {argument}{space_after}'),
                SourceExpectation.source_is_not_at_end(current_line_number=1,
                                                       remaining_part_of_current_line=space_after[1:])
            ),
            SourceCase(
                'expression is followed by non-expression',
                source('  {primitive_with_arg}    {argument} {token_after}'),
                SourceExpectation.source_is_not_at_end(current_line_number=1,
                                                       remaining_part_of_current_line=token_after)
            ),
            SourceCase(
                '( primitive )',
                source('( {primitive_with_arg} {argument} )'),
                SourceExpectation.is_at_end_of_line(1),
            ),
            SourceCase(
                'primitive, within parentheses, with tokens on separate lines',
                source('( \n {primitive_with_arg} \n {argument} \n )'),
                SourceExpectation.is_at_end_of_line(4),
            ),
            SourceCase(
                'primitive, within parentheses, with expression tokens on separate lines, followed by non-expression',
                source('( \n {primitive_with_arg} \n {argument} \n ) {token_after}'),
                SourceExpectation.source_is_not_at_end(current_line_number=4,
                                                       remaining_part_of_current_line=token_after),
            ),
            SourceCase(
                '( ( primitive ) )',
                source('( ( {primitive_with_arg} {argument} ) )'),
                SourceExpectation.is_at_end_of_line(1),
            ),
        ]

        # ACT & ASSERT #

        parse_check.check_with_must_be_on_current_line_variants(
            self,
            self.parser_maker,
            ast.PrimitiveWithArg(the_argument),
            GRAMMARS,
            cases,
        )

    def test_fail__expr_on_following_line_is_accepted(self):
        cases = [
            NameAndValue(
                'token is not the name of a primitive expression',
                ast.NOT_A_PRIMITIVE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME,
            ),
            NameAndValue(
                'token is the name of a primitive expression, but it is quoted/soft',
                str(surrounded_by_soft_quotes(ast.PRIMITIVE_SANS_ARG)),
            ),
            NameAndValue(
                'token is the name of a primitive expression, but it is quoted/hard',
                str(surrounded_by_hard_quotes(ast.PRIMITIVE_SANS_ARG)),
            ),
        ]
        parse_check.check_fail__expr_on_following_line_is_accepted(
            self,
            self.parser_maker,
            GRAMMARS,
            cases,
        )

    def test_fail__must_be_on_current_line(self):
        cases = [
            NameAndValue(
                'token is not the name of a primitive expression',
                [ast.NOT_A_PRIMITIVE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME],
            ),
            NameAndValue(
                'token is the name of a primitive expression, but it is quoted/soft',
                [str(surrounded_by_soft_quotes(ast.PRIMITIVE_SANS_ARG))],
            ),
            NameAndValue(
                'token is the name of a primitive expression, but it is quoted/hard',
                [str(surrounded_by_hard_quotes(ast.PRIMITIVE_SANS_ARG))],
            ),
            NameAndValue(
                'token is the name of a primitive expression, but it is on the next line',
                [ast.PRIMITIVE_SANS_ARG],
            ),
        ]
        # ACT & ASSERT #
        parse_check.check_fail__must_be_on_current_line(
            self,
            self.parser_maker,
            GRAMMARS,
            cases,
        )


class TestSinglePrefixOpExpression(_TextCaseWithParserVariantsBase, ABC):
    PREFIX_OPERATORS = [
        (
            ast.PREFIX_P,
            ast.PrefixOpExprP,
        ),
        (
            ast.PREFIX_Q,
            ast.PrefixOpExprQ,
        ),
    ]

    def test_successful_parse_with_primitive_expr(self):

        space_after = '           '
        token_after = str(surrounded_by_hard_quotes('not an expression'))

        primitive_expr = ast.PrimitiveSansArg()
        primitive_expr_src = ast.PRIMITIVE_SANS_ARG

        def cases_for_operator(the_prefix_operator: str) -> List[SourceCase]:
            sf = StringFormatter({
                'op': the_prefix_operator,
                'primitive_expr': primitive_expr_src,
                'space_after': space_after,
                'token_after': token_after,
            })
            return [
                SourceCase(
                    'first line is only primitive expr',
                    sf.format('{op} {primitive_expr}'),
                    SourceExpectation.is_at_end_of_line(1)
                ),
                SourceCase(
                    'first line is primitive expr with space around',
                    sf.format(' {op}  {primitive_expr}{space_after}'),
                    SourceExpectation.source_is_not_at_end(current_line_number=1,
                                                           remaining_part_of_current_line=space_after[1:])
                ),
                SourceCase(
                    'expression is followed by non-expression',
                    sf.format('{op} {primitive_expr} {token_after}'),
                    SourceExpectation.source_is_not_at_end(current_line_number=1,
                                                           remaining_part_of_current_line=token_after)
                ),
                SourceCase(
                    '( op primitive )',
                    sf.format('( {op} {primitive_expr} )'),
                    SourceExpectation.is_at_end_of_line(1),
                ),
                SourceCase(
                    'op ( primitive )',
                    sf.format('{op} ( {primitive_expr} )'),
                    SourceExpectation.is_at_end_of_line(1),
                ),
                SourceCase(
                    'no source after operator, but expr on following line',
                    sf.format('{op}\n{primitive_expr}'),
                    SourceExpectation.is_at_end_of_line(2),
                ),
            ]

        operator_cases = [
            (prefix_operator,
             mk_prefix_expr(primitive_expr),
             cases_for_operator(prefix_operator))
            for prefix_operator, mk_prefix_expr in self.PREFIX_OPERATORS
        ]

        for grammar in GRAMMARS:
            for operator_case in operator_cases:
                cases = current_line_case_variants_for_grammar(operator_case[1],
                                                               grammar.value,
                                                               operator_case[2])
                for case in cases:
                    with self.subTest(grammar=grammar.name,
                                      prefix_operator=operator_case[0],
                                      name=case.name):
                        parse_check.check(
                            self,
                            self.parser_maker,
                            case.arrangement,
                            case.expectation,
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
                            non_expr=str(surrounded_by_soft_quotes(ast.PRIMITIVE_SANS_ARG)))),
                    ),
                ]
                for case in cases:
                    with self.subTest(grammar=grammar_description,
                                      prefix_operator=prefix_operator,
                                      case_name=case.name):
                        parser = self.parser_maker.make(grammar, must_be_on_current_line=True)
                        with self.assertRaises(SingleInstructionInvalidArgumentException):
                            parser.parse(case.value)


class TestSingleRefExpression(_TextCaseWithParserVariantsBase, ABC):
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
                    name('first line is only primitive expr'),
                    source('{symbol_name}'),
                    SourceExpectation.is_at_end_of_line(1)
                ),
                SourceCase(
                    name('first line is primitive expr with space around'),
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

        parse_check.check_with_must_be_on_current_line_variants(
            self,
            self.parser_maker,
            expected_expression=ast.RefExpr(symbol_name),
            grammars=GRAMMARS,
            original_source_cases=source_cases,
        )

    def test_token_SHOULD_be_interpreted_as_sym_ref_WHEN_sym_ref_syntax_is_used_for_existing_primitive(self):
        for grammar_description, grammar in GRAMMARS:
            with self.subTest(grammar=grammar_description):
                parse_check.check(
                    self,
                    self.parser_maker,
                    Arrangement(
                        grammar=grammar,
                        source=remaining_source(
                            symbol_reference_syntax_for_name(ast.PRIMITIVE_SANS_ARG)
                        ),
                    ),
                    Expectation(
                        expression=ast.RefExpr(ast.PRIMITIVE_SANS_ARG),
                        source=asrt_source.is_at_end_of_line(1),
                    ),
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
                    parser = self.parser_maker.make(grammar, must_be_on_current_line=True)
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        parser.parse(case.value)
