import unittest
from abc import ABC, abstractmethod
from typing import Sequence, List

from exactly_lib.impls.types.expression import parser as sut
from exactly_lib.impls.types.expression.grammar import Grammar, EXPR
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import Parser
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.expression.test_resources import test_grammars as ast
from exactly_lib_test.impls.types.expression.test_resources.case_generation import \
    current_line_case_variants_for_grammar
from exactly_lib_test.impls.types.expression.test_resources.ex_arr import Arrangement, Expectation, SourceCase
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source_string, remaining_source
from exactly_lib_test.test_resources.test_utils import NArrEx


class ParserMaker(ABC):
    @abstractmethod
    def make(self,
             grammar: Grammar[EXPR],
             must_be_on_current_line: bool,
             ) -> Parser[EXPR]:
        pass


class _ParserMakerOfFullExprParser(ParserMaker):
    def make(self,
             grammar: Grammar[EXPR],
             must_be_on_current_line: bool,
             ) -> Parser[EXPR]:
        return sut.parsers(grammar, must_be_on_current_line).full


class _ParserMakerOfSimpleExprParser(ParserMaker):
    def make(self,
             grammar: Grammar[EXPR],
             must_be_on_current_line: bool,
             ) -> Parser[EXPR]:
        return sut.parsers(grammar, must_be_on_current_line).simple


PARSER_MAKER_OF_FULL_EXPR_PARSER = _ParserMakerOfFullExprParser()
PARSER_MAKER_OF_SIMPLE_EXPR_PARSER = _ParserMakerOfSimpleExprParser()


def check(put: unittest.TestCase,
          parser_maker: ParserMaker,
          arrangement: Arrangement,
          expectation: Expectation,
          ):
    parser = parser_maker.make(arrangement.grammar, arrangement.must_be_on_current_line)
    actual = parser.parse(arrangement.source)
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


def check__multi(put: unittest.TestCase,
                 parser_maker: ParserMaker,
                 cases: Sequence[NArrEx[Arrangement, Expectation]],
                 ):
    for case in cases:
        with put.subTest(name=case.name):
            check(
                put,
                parser_maker,
                case.arrangement,
                case.expectation,
            )


def check_with_must_be_on_current_line_variants(
        put: unittest.TestCase,
        parser_maker: ParserMaker,
        expected_expression: ast.Expr,
        grammars: Sequence[NameAndValue[Grammar]],
        original_source_cases: Sequence[SourceCase],
):
    grammar_cases = [
        NameAndValue(
            the_grammar.name,
            current_line_case_variants_for_grammar(expected_expression,
                                                   the_grammar.value,
                                                   original_source_cases)
        )
        for the_grammar in grammars
    ]

    for grammar_case in grammar_cases:
        for source_case in grammar_case.value:
            with put.subTest(grammar=grammar_case.name,
                             name=source_case.name):
                check(
                    put,
                    parser_maker,
                    source_case.arrangement,
                    source_case.expectation,
                )


def check_fail__expr_on_following_line_is_accepted(put: unittest.TestCase,
                                                   parser_maker: ParserMaker,
                                                   grammars: List[NameAndValue[Grammar]],
                                                   cases: Sequence[NameAndValue[str]]
                                                   ):
    for grammar_case in grammars:
        for case in cases:
            # Source is on first line
            for must_be_on_current_line in [False, True]:
                with put.subTest(grammar=grammar_case.name,
                                 case_name=case.name,
                                 source='is on first line',
                                 must_be_on_current_line=must_be_on_current_line):
                    # ACT & ASSERT #
                    parse_source = remaining_source_string(case.value)
                    parser = parser_maker.make(grammar_case.value,
                                               must_be_on_current_line=must_be_on_current_line)
                    with put.assertRaises(SingleInstructionInvalidArgumentException):
                        parser.parse(parse_source)
            # Source is not on first line
            with put.subTest(grammar=grammar_case.name,
                             case_name=case.name,
                             source='is not on first line',
                             must_be_on_current_line=must_be_on_current_line):
                parse_source = remaining_source_string('\n' + case.value)
                parser = parser_maker.make(grammar_case.value,
                                           must_be_on_current_line=must_be_on_current_line)
                with put.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(parse_source)


def check_fail__must_be_on_current_line(put: unittest.TestCase,
                                        parser_maker: ParserMaker,
                                        grammars: List[NameAndValue[Grammar]],
                                        cases_w_lines_after_empty_line: Sequence[NameAndValue[List[str]]],
                                        ):
    for grammar_case in grammars:
        parser = parser_maker.make(grammar_case.value, must_be_on_current_line=True)
        for case in cases_w_lines_after_empty_line:
            with put.subTest(grammar=grammar_case.name,
                             case_name=case.name):
                source = remaining_source('', case.value)
                with put.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(source)
