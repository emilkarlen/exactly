import unittest

from exactly_lib.instructions.multi_phase import define_symbol as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.instructions.multi_phase.define_symbol.test_case_base import TestCaseBaseForParser
from exactly_lib_test.instructions.multi_phase.define_symbol.test_resources import *
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.resolver_structure_assertions import matches_container
from exactly_lib_test.symbol.test_resources.symbol_syntax import NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources import arguments_building as arg_syntax
from exactly_lib_test.test_case_utils.string_matcher.test_resources.assertions import matches_string_matcher_resolver
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulScenarios),
        unittest.makeSuite(TestUnsuccessfulScenarios),
    ])


class TestSuccessfulScenarios(TestCaseBaseForParser):
    def test_successful_parse_of_arbitrary_matcher(self):
        defined_name = 'defined_name'

        # ARRANGE #

        source = single_line_source(
            src('{string_matcher_type} {defined_name} = {matcher_argument}',
                defined_name=defined_name,
                matcher_argument=arg_syntax.arbitrary_single_line_value_that_must_not_be_quoted()),
        )

        # EXPECTATION #

        expected_container = matches_container(
            matches_string_matcher_resolver()
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


class TestUnsuccessfulScenarios(TestCaseBaseForParser):
    def test_failing_parse(self):
        cases = [
            (
                'missing argument',
                '',
            ),
            (
                'single quoted argument',
                str(surrounded_by_hard_quotes(arg_syntax.arbitrary_single_line_value_that_must_not_be_quoted())),
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
                    src('{string_matcher_type} {defined_name} = {matcher_argument}',
                        defined_name=defined_name,
                        matcher_argument=rhs_source),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    # ACT & ASSERT #
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
