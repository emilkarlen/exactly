import unittest

from typing import Optional

from exactly_lib.instructions.multi_phase import define_symbol as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol import lookups
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.string_matcher.string_matchers import StringMatcherConstant
from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment
from exactly_lib.type_system.logic.string_matcher import StringMatcher, FileToCheck
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.string import lines_content
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.multi_phase.define_symbol.test_case_base import TestCaseBaseForParser
from exactly_lib_test.instructions.multi_phase.define_symbol.test_resources import *
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.resolver_structure_assertions import matches_container
from exactly_lib_test.symbol.test_resources.string_matcher import is_reference_to_string_matcher, \
    StringMatcherResolverConstantTestImpl
from exactly_lib_test.symbol.test_resources.symbol_syntax import NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case_utils.condition.integer.test_resources.arguments_building import int_condition
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources import arguments_building as arg_syntax
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.arguments_building import \
    ImplicitActualFileArgumentsConstructor
from exactly_lib_test.test_case_utils.string_matcher.test_resources import model_construction
from exactly_lib_test.test_case_utils.string_matcher.test_resources.assertions import matches_string_matcher_resolver
from exactly_lib_test.test_case_utils.test_resources import matcher_assertions
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase, \
    MessageBuilder
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

    def test_successful_parse_of_reference(self):
        defined_name = 'defined_name'

        referenced_symbol = NameAndValue('referenced_name',
                                         ARBITRARY_RESOLVER)

        symbols = SymbolTable({
            referenced_symbol.name:
                symbol_utils.container(referenced_symbol.value)
        })

        # ARRANGE #

        source = single_line_source(
            src('{string_matcher_type} {defined_name} = {matcher_argument}',
                defined_name=defined_name,
                matcher_argument=referenced_symbol.name),
        )

        arrangement = ArrangementWithSds()

        # EXPECTATION #

        expected_container = matches_container(
            matches_string_matcher_resolver(
                references=asrt.matches_sequence([
                    is_reference_to_string_matcher(referenced_symbol.name)
                ]),
                symbols=symbols)
        )

        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                asrt_sym_usage.matches_definition(asrt.equals(defined_name),
                                                  expected_container),
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                defined_name,
                expected_container,
            )
        )

        # ACT & ASSERT #

        self._check(source, arrangement, expectation)

    def test_successful_parse_and_application_of_non_trivial_matcher(self):
        defined_name = 'defined_name'

        expected_container = matches_container(
            matches_string_matcher_resolver()
        )

        not_num_lines_eq_1_matcher_arg = self._not_num_lines_eq_1_matcher_arg()

        cases = [
            NEA('should match',
                expected=matcher_assertions.is_matching_success(),
                actual=lines_content([
                    '1st line',
                    '2nd line',
                ])
                ),
            NEA('should not match',
                expected=matcher_assertions.arbitrary_matching_failure(),
                actual='a single line'
                ),
        ]

        for case in cases:
            source = single_line_source(
                src('{string_matcher_type} {defined_name} = {matcher_argument}',
                    defined_name=defined_name,
                    matcher_argument=not_num_lines_eq_1_matcher_arg),
            )
            expectation = Expectation(
                symbol_usages=asrt.matches_sequence([
                    asrt_sym_usage.matches_definition(asrt.equals(defined_name),
                                                      expected_container)
                ]),
                symbols_after_main=assert_symbol_table_is_singleton(
                    defined_name,
                    expected_container,
                ),
                assertion_on_instruction_environment=
                AssertApplicationOfMatcherInSymbolTable(defined_name,
                                                        actual_model_contents=case.actual,
                                                        expected_matcher_result=case.expected),
            )

            with self.subTest(case.name):
                # ACT & ASSERT #
                self._check(source, ArrangementWithSds(), expectation)

    @staticmethod
    def _not_num_lines_eq_1_matcher_arg() -> str:
        eq_1_condition = int_condition(comparators.EQ, 1)
        num_lines_eq_1_matcher = arg_syntax.NumLinesAssertionArgumentsConstructor(eq_1_condition)
        num_lines_eq_1_arg_constructor = ImplicitActualFileArgumentsConstructor(
            arg_syntax.CommonArgumentsConstructor(),
            num_lines_eq_1_matcher,
        )
        return num_lines_eq_1_arg_constructor.apply(ExpectationType.NEGATIVE)


class TestUnsuccessfulScenarios(TestCaseBaseForParser):
    def test_failing_parse(self):
        cases = [
            NameAndValue(
                'missing argument',
                '',
            ),
            NameAndValue(
                'single quoted argument',
                str(surrounded_by_hard_quotes(arg_syntax.arbitrary_single_line_value_that_must_not_be_quoted())),
            ),
            NameAndValue(
                'non-transformer name that is not a valid symbol name',
                NOT_A_VALID_SYMBOL_NAME,
            ),
        ]
        # ARRANGE #
        defined_name = 'defined_name'
        parser = sut.EmbryoParser()
        for case in cases:
            with self.subTest(case.name):
                source = single_line_source(
                    src('{string_matcher_type} {defined_name} = {matcher_argument}',
                        defined_name=defined_name,
                        matcher_argument=case.value),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    # ACT & ASSERT #
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


class AssertApplicationOfMatcherInSymbolTable(ValueAssertionBase[InstructionEnvironmentForPostSdsStep]):
    def __init__(self,
                 matcher_symbol_name: str,
                 actual_model_contents: str,
                 expected_matcher_result: Optional[ValueAssertion[str]]):
        self.matcher_symbol_name = matcher_symbol_name
        self.actual_model_contents = actual_model_contents
        self.expected_matcher_result = expected_matcher_result

    def _apply(self,
               put: unittest.TestCase,
               value: InstructionEnvironmentForPostSdsStep,
               message_builder: MessageBuilder):
        model = self._new_model(value)
        matcher_to_apply = self._get_matcher(value)

        result = matcher_to_apply.matches(model)

        if self.expected_matcher_result is None:
            put.assertIsNone(result,
                             'result from main')
        else:
            put.assertIsNotNone(result,
                                'result from main')
            err_msg_env = ErrorMessageResolvingEnvironment(value.home_and_sds,
                                                           value.symbols)
            err_msg = result.resolve(err_msg_env)
            self.expected_matcher_result.apply_with_message(put, err_msg,
                                                            'error result of main')

    def _get_matcher(self, environment: InstructionEnvironmentForPostSdsStep) -> StringMatcher:
        matcher_resolver = lookups.lookup_string_matcher(environment.symbols, self.matcher_symbol_name)
        return matcher_resolver.resolve(environment.symbols).value_of_any_dependency(environment.home_and_sds)

    def _new_model(self, environment: InstructionEnvironmentForPostSdsStep) -> FileToCheck:
        model_builder = model_construction.model_of(self.actual_model_contents)
        return model_construction.ModelConstructor(model_builder, environment.sds).construct()


ARBITRARY_RESOLVER = StringMatcherResolverConstantTestImpl(StringMatcherConstant(None),
                                                           [])

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
