import unittest
from typing import Sequence

from exactly_lib.impls.types.expression import parser as sut
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.expression.test_resources.infix_op_precedence_grammar import Expr, GRAMMAR
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_resources.test_utils import NIE


def check__simple_and_full__multi(put: unittest.TestCase,
                                  source_and_expectation_cases: Sequence[NIE[str, Expr]]):
    # ARRANGE #
    expected_source = asrt_source.is_at_end_of_line(1)
    for case in source_and_expectation_cases:
        for parser_case in _PARSER_CASES:
            with put.subTest(case.name,
                             parser_case=parser_case.name):
                source = remaining_source(case.input_value)
                # ACT #
                actual = parser_case.value.parse(source)
                # ASSERT #
                expected_source.apply_with_message(put, source, 'source')
                put.assertEqual(case.expected_value, actual, 'parsed expression')


def check__full_and_simple_within_parenthesis__multi(put: unittest.TestCase,
                                                     source_and_expectation_cases: Sequence[NIE[str, Expr]]):
    # ARRANGE #
    expected_source = asrt_source.is_at_end_of_line(1)
    for case in source_and_expectation_cases:
        with put.subTest(case.name,
                         parser_case='full',
                         source=case.input_value):
            source = remaining_source(case.input_value)
            # ACT #
            actual = _PARSER__FULL.parse(source)
            # ASSERT #
            expected_source.apply_with_message(put, source, 'source')
            put.assertEqual(case.expected_value, actual, 'parsed expression')

        with put.subTest(case.name,
                         parser_case='simple, within parenthesis',
                         source=case.input_value):
            source = remaining_source(' '.join(['(', case.input_value, ')']))
            # ACT #
            actual = _PARSER__SIMPLE.parse(source)
            # ASSERT #
            expected_source.apply_with_message(put, source, 'source')
            put.assertEqual(case.expected_value, actual, 'parsed expression')


_PARSERS = sut.parsers(GRAMMAR)
_PARSER__FULL = _PARSERS.full
_PARSER__SIMPLE = _PARSERS.simple


def _parser_cases__for_typing() -> Sequence[NameAndValue[Parser[Expr]]]:
    return [
        NameAndValue('full', _PARSER__FULL),
        NameAndValue('simple', _PARSER__SIMPLE),
    ]


_PARSER_CASES = _parser_cases__for_typing()
