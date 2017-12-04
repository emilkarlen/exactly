import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import from_parse_source
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.condition.integer import parse_integer_condition as sut
from exactly_lib.test_case_utils.condition.integer.integer_matcher import IntegerMatcher, \
    IntegerMatcherFromComparisonOperator
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources.matcher_assertions import is_equivalent_to, ModelInfo


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseIntegerMatcher),
    ])


_NAME_OF_LHS = 'LHS'


class Case:
    def __init__(self,
                 name: str,
                 source,
                 source_assertion: asrt.ValueAssertion,
                 result_assertion: asrt.ValueAssertion):
        self.name = name
        self.source = source
        self.source_assertion = source_assertion
        self.result_assertion = result_assertion


class TestParseIntegerMatcher(unittest.TestCase):
    def test_failing_parse(self):
        cases = [
            (
                'no arguments',
                remaining_source(''),
            ),
            (
                'no arguments, but it appears on the following line',
                remaining_source('',
                                 ['= 1']),
            ),
            (
                'invalid OPERATOR',
                remaining_source('- 72'),
            ),
            (
                'quoted OPERATOR',
                remaining_source('"=" 69'),
            ),
            (
                'missing INTEGER',
                remaining_source('='),
            ),
            (
                'missing INTEGER, but it appears on following line',
                remaining_source('=',
                                 ['72']),
            ),
            (
                'invalid INTEGER',
                remaining_source('= 0.5'),
            ),
            (
                'invalid INTEGER expression',
                remaining_source('= "1 + [50]"'),
            ),
        ]
        for name, source in cases:
            with self.subTest(case_name=name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    with from_parse_source(source) as parser:
                        sut.parse_integer_matcher(parser)

    def test_successful_parse(self):
        # ARRANGE #
        cases = [
            Case('= plain integer',
                 remaining_source('= 1'),
                 source_assertion=
                 assert_source(is_at_eol=asrt.is_true),
                 result_assertion=is_equivalent_to(matcher_of(comparators.EQ, 1),
                                                   [
                                                       model_of(-1),
                                                       model_of(1),
                                                       model_of(2),
                                                   ])),
            Case('!=',
                 remaining_source('!= 1'),
                 source_assertion=
                 assert_source(is_at_eol=asrt.is_true),
                 result_assertion=is_equivalent_to(matcher_of(comparators.NE, 1),
                                                   [
                                                       model_of(-1),
                                                       model_of(1),
                                                       model_of(2),
                                                   ])),
            Case('<',
                 remaining_source('< 69'),
                 source_assertion=
                 assert_source(is_at_eol=asrt.is_true),
                 result_assertion=is_equivalent_to(matcher_of(comparators.LT, 69),
                                                   [
                                                       model_of(60),
                                                       model_of(69),
                                                       model_of(72),
                                                   ])),
            Case('<=',
                 remaining_source('<= 69'),
                 source_assertion=
                 assert_source(is_at_eol=asrt.is_true),
                 result_assertion=is_equivalent_to(matcher_of(comparators.LTE, 69),
                                                   [
                                                       model_of(60),
                                                       model_of(69),
                                                       model_of(72),
                                                   ])),
            Case('>',
                 remaining_source('> 69'),
                 source_assertion=
                 assert_source(is_at_eol=asrt.is_true),
                 result_assertion=is_equivalent_to(matcher_of(comparators.GT, 69),
                                                   [
                                                       model_of(60),
                                                       model_of(69),
                                                       model_of(72),
                                                   ])),
            Case('>=',
                 remaining_source('>= 69'),
                 source_assertion=
                 assert_source(is_at_eol=asrt.is_true),
                 result_assertion=is_equivalent_to(matcher_of(comparators.GTE, 69),
                                                   [
                                                       model_of(60),
                                                       model_of(69),
                                                       model_of(72),
                                                   ])),
            Case('>= following content on line',
                 remaining_source('>= 72 next'),
                 source_assertion=
                 assert_source(remaining_part_of_current_line=asrt.equals('next')),
                 result_assertion=is_equivalent_to(matcher_of(comparators.GTE, 72),
                                                   [
                                                       model_of(69),
                                                       model_of(72),
                                                       model_of(80),
                                                   ])),
            Case('= integer expression',
                 remaining_source('= "69+72"'),
                 source_assertion=
                 assert_source(is_at_eol=asrt.is_true),
                 result_assertion=is_equivalent_to(matcher_of(comparators.EQ, 69 + 72),
                                                   [
                                                       model_of(69 + 72 - 1),
                                                       model_of(69 + 72),
                                                       model_of(69 + 72 + 1),
                                                   ])),
        ]
        for case in cases:
            with from_parse_source(case.source) as parser:
                # ACT #
                actual = sut.parse_integer_matcher(parser, _NAME_OF_LHS)
                # ASSERT #
            case.source_assertion.apply_with_message(self, case.source, 'source')
            case.result_assertion.apply_with_message(self, actual, 'parsed value')


def model_of(rhs: int) -> ModelInfo:
    return ModelInfo(rhs)


def matcher_of(operator: comparators.ComparisonOperator,
               constant_rhs: int) -> IntegerMatcher:
    return IntegerMatcherFromComparisonOperator(_NAME_OF_LHS,
                                                operator,
                                                constant_rhs)
