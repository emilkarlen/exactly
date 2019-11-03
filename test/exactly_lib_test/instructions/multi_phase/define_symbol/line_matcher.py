import re
import unittest

import exactly_lib.definitions.primitives.line_matcher
from exactly_lib.instructions.multi_phase import define_symbol as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherConstant, LineMatcherAnd, LineMatcherRegex
from exactly_lib.test_case_utils.line_matcher.resolvers import LineMatcherConstantResolver
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.multi_phase.define_symbol.test_resources import *
from exactly_lib_test.instructions.multi_phase.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.line_matcher import is_line_matcher_reference_to
from exactly_lib_test.symbol.test_resources.resolver_structure_assertions import matches_container
from exactly_lib_test.symbol.test_resources.symbol_syntax import NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case_utils.line_matcher.test_resources import argument_syntax
from exactly_lib_test.test_case_utils.line_matcher.test_resources import value_assertions as asrt_line_matcher
from exactly_lib_test.test_case_utils.line_matcher.test_resources.resolver_assertions import \
    resolved_value_matches_line_matcher
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources import matcher_assertions as asrt_matcher
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulScenarios),
        unittest.makeSuite(TestUnsuccessfulScenarios),
    ])


class TestCaseBase(unittest.TestCase):
    def _check(self,
               source: ParseSource,
               arrangement: ArrangementWithSds,
               expectation: Expectation,
               ):
        parser = sut.EmbryoParser()
        embryo_check.check(self, parser, source, arrangement, expectation)


class TestSuccessfulScenarios(TestCaseBase):
    def test_successful_parse_WHEN_rhs_is_empty_THEN_result_SHOULD_be_constant_True_matcher(self):
        defined_name = 'defined_name'

        # ARRANGE #

        source = single_line_source(
            src('{line_match_type} {defined_name} = ',
                defined_name=defined_name),
        )

        # EXPECTATION #

        expected_equivalent = LineMatcherConstant(True)
        models_for_equivalence_check = [
            asrt_matcher.ModelInfo((1, '')),
            asrt_matcher.ModelInfo((1, '  ')),
            asrt_matcher.ModelInfo((1, 'non empty')),
            asrt_matcher.ModelInfo((2, '')),
            asrt_matcher.ModelInfo((2, '  ')),
            asrt_matcher.ModelInfo((3, 'non empty')),
        ]

        expected_container = matches_container(
            resolved_value_matches_line_matcher(
                asrt_line_matcher.value_matches_line_matcher(
                    asrt_matcher.is_equivalent_to(expected_equivalent,
                                                  models_for_equivalence_check)
                )
            )
        )

        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                asrt_sym_usage.matches_definition(asrt.equals(defined_name),
                                                  expected_container)
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                defined_name,
                expected_container,
            )
        )

        # ACT & ASSERT #

        self._check(source, ArrangementWithSds(), expectation)

    def test_successful_parse_of_regex(self):
        # ARRANGE #

        regex_str = 'the_regex'
        models_for_equivalence_check = [
            asrt_matcher.ModelInfo((1, regex_str)),
            asrt_matcher.ModelInfo((2, 'before' + regex_str + 'after')),
            asrt_matcher.ModelInfo((1, 'no match')),
        ]

        symbol = NameAndValue('the_symbol_name',
                              LineMatcherConstant(True))

        regex_matcher_syntax = argument_syntax.syntax_for_regex_matcher(regex_str)

        matcher_argument = argument_syntax.syntax_for_and([
            symbol.name,
            regex_matcher_syntax,
        ])

        defined_name = 'defined_name'

        source = remaining_source(
            src('{line_match_type} {defined_name} = {matcher_argument}',
                defined_name=defined_name,
                matcher_argument=matcher_argument),
            following_lines=['following line'],
        )

        # EXPECTATION #

        the_regex_matcher = LineMatcherRegex(re.compile(regex_str))
        the_and_matcher = LineMatcherAnd([
            symbol.value,
            the_regex_matcher,
        ])

        expected_container = matches_container(
            assertion_on_resolver=
            resolved_value_matches_line_matcher(
                asrt_line_matcher.value_matches_line_matcher(
                    asrt_matcher.is_equivalent_to(the_and_matcher,
                                                  models_for_equivalence_check)
                ),
                references=asrt.matches_sequence([
                    is_line_matcher_reference_to(symbol.name),
                ]),
                symbols=SymbolTable({
                    symbol.name: container(LineMatcherConstantResolver(symbol.value)),
                }),
            )
        )

        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                asrt_sym_usage.matches_definition(asrt.equals(defined_name),
                                                  expected_container)
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                defined_name,
                expected_container,
            )
        )

        # ACT & ASSERT #

        self._check(source, ArrangementWithSds(), expectation)


class TestUnsuccessfulScenarios(TestCaseBase):
    def test_failing_parse(self):
        cases = [
            (
                'single quoted argument',
                str(surrounded_by_hard_quotes(exactly_lib.definitions.primitives.line_matcher.REGEX_MATCHER_NAME)),
            ),
            (
                'non-transformer name that is not a valid symbol name',
                NOT_A_VALID_SYMBOL_NAME,
            ),
        ]
        # ARRANGE #
        defined_name = 'defined_name'
        parser = sut.EmbryoParser()
        for name, rhs_source in cases:
            with self.subTest(name=name):
                source = single_line_source(
                    src('{line_match_type} {defined_name} = {matcher_argument}',
                        defined_name=defined_name,
                        matcher_argument=rhs_source),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    # ACT & ASSERT #
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
