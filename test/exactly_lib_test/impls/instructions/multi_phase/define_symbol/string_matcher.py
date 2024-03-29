import unittest

from exactly_lib.impls.instructions.multi_phase.define_symbol import parser as sut
from exactly_lib.impls.instructions.utils.logic_type_resolving_helper import resolving_helper_for_instruction_env
from exactly_lib.impls.types.condition import comparators
from exactly_lib.impls.types.matcher.impls.constant import MatcherWithConstantResult
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.type_val_deps.sym_ref import symbol_lookup
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.type_val_prims.matcher.string_matcher import StringMatcher
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources import matcher_helpers
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.embryo_checker import \
    INSTRUCTION_CHECKER
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.source_formatting import *
from exactly_lib_test.impls.instructions.multi_phase.test_resources.embryo_arr_exp import \
    InstructionApplicationEnvironment, Arrangement, Expectation
from exactly_lib_test.impls.types.integer.test_resources.arguments_building import int_condition
from exactly_lib_test.impls.types.string_matcher.test_resources import arguments_building as arg_syntax
from exactly_lib_test.impls.types.string_matcher.test_resources.arguments_building import \
    ImplicitActualFileArgumentsConstructor
from exactly_lib_test.impls.types.string_source.test_resources import model_constructor
from exactly_lib_test.impls.types.test_resources import matcher_assertions
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.symbol_syntax import NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.dep_variants.test_resources.type_sdv_assertions import \
    matches_sdv_of_string_matcher
from exactly_lib_test.type_val_deps.sym_ref.test_resources.container_assertions import matches_container
from exactly_lib_test.type_val_deps.types.string_matcher.test_resources.string_matchers import \
    string_matcher_sdv_constant_test_impl
from exactly_lib_test.type_val_deps.types.string_matcher.test_resources.symbol_context import StringMatcherSymbolContext
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulScenarios),
        unittest.makeSuite(TestUnsuccessfulScenarios),
    ])


class TestSuccessfulScenarios(unittest.TestCase):
    def test_successful_parse_of_arbitrary_matcher(self):
        defined_name = 'defined_name'

        # ARRANGE #

        argument_cases = [
            NameAndValue('value on same line',
                         '{matcher_argument}'
                         ),
            NameAndValue('value on following line',
                         '{new_line} {matcher_argument}'
                         ),
        ]

        for argument_case in argument_cases:
            with self.subTest(argument_case.name):
                source = single_line_source(
                    src2(ValueType.STRING_MATCHER, defined_name, argument_case.value,
                         matcher_argument=arg_syntax.arbitrary_single_line_value_that_must_not_be_quoted()),
                )

                # EXPECTATION #

                expected_container = matches_container(
                    asrt.equals(ValueType.STRING_MATCHER),
                    matches_sdv_of_string_matcher()
                )

                expectation = Expectation.phase_agnostic(
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

                INSTRUCTION_CHECKER.check(self, source, Arrangement.phase_agnostic(), expectation)

    def test_successful_parse_of_reference(self):
        defined_name = 'defined_name'

        referenced_symbol = StringMatcherSymbolContext.of_arbitrary_value('referenced_name')

        symbols = referenced_symbol.symbol_table

        # ARRANGE #

        source = single_line_source(
            src2(ValueType.STRING_MATCHER, defined_name, referenced_symbol.name),
        )

        arrangement = Arrangement.phase_agnostic()

        # EXPECTATION #

        expected_container = matches_container(
            asrt.equals(ValueType.STRING_MATCHER),
            matches_sdv_of_string_matcher(
                references=asrt.matches_sequence([
                    referenced_symbol.reference_assertion
                ]),
                symbols=symbols)
        )

        expectation = Expectation.phase_agnostic(
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

        INSTRUCTION_CHECKER.check(self, source, arrangement, expectation)

    def test_matcher_SHOULD_be_parsed_as_full_expression(self):
        matcher_helpers.check_matcher_should_be_parsed_as_full_expression(
            self,
            StringMatcherSymbolContext.of_arbitrary_value('symbol_1'),
            StringMatcherSymbolContext.of_arbitrary_value('symbol_2'),
            ValueType.STRING_MATCHER,
        )

    def test_successful_parse_and_application_of_non_trivial_matcher(self):
        defined_name = 'defined_name'

        expected_container = matches_container(
            asrt.equals(ValueType.STRING_MATCHER),
            matches_sdv_of_string_matcher()
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
                expected=matcher_assertions.is_arbitrary_matching_failure(),
                actual='a single line'
                ),
        ]

        for case in cases:
            source = single_line_source(
                src2(ValueType.STRING_MATCHER,
                     defined_name,
                     not_num_lines_eq_1_matcher_arg),
            )
            expectation = Expectation.phase_agnostic(
                symbol_usages=asrt.matches_sequence([
                    asrt_sym_usage.matches_definition(asrt.equals(defined_name),
                                                      expected_container)
                ]),
                symbols_after_main=assert_symbol_table_is_singleton(
                    defined_name,
                    expected_container,
                ),
                instruction_environment=
                AssertApplicationOfMatcherInSymbolTable(self,
                                                        defined_name,
                                                        actual_model_contents=case.actual,
                                                        expected_matcher_result=case.expected),
            )

            with self.subTest(case.name):
                # ACT & ASSERT #
                INSTRUCTION_CHECKER.check(self, source, Arrangement.phase_agnostic(), expectation)

    @staticmethod
    def _not_num_lines_eq_1_matcher_arg() -> str:
        eq_1_condition = int_condition(comparators.EQ, 1)
        num_lines_eq_1_matcher = arg_syntax.NumLinesAssertionArgumentsConstructor(eq_1_condition)
        num_lines_eq_1_arg_constructor = ImplicitActualFileArgumentsConstructor(
            arg_syntax.CommonArgumentsConstructor(),
            num_lines_eq_1_matcher,
        )
        return num_lines_eq_1_arg_constructor.apply(ExpectationType.NEGATIVE)


class TestUnsuccessfulScenarios(unittest.TestCase):
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
                    src2(ValueType.STRING_MATCHER, defined_name, case.value),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    # ACT & ASSERT #
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


class AssertApplicationOfMatcherInSymbolTable(matcher_helpers.AssertApplicationOfMatcherInSymbolTable):
    def __init__(self,
                 put: unittest.TestCase,
                 matcher_symbol_name: str,
                 actual_model_contents: str,
                 expected_matcher_result: Assertion[MatchingResult]):
        super().__init__(matcher_symbol_name,
                         expected_matcher_result)
        self.put = put
        self.actual_model_contents = actual_model_contents

    def _apply_matcher(self,
                       environment: InstructionApplicationEnvironment) -> MatchingResult:
        matcher_to_apply = self._get_matcher(environment)
        model = self._new_model(environment.instruction)
        return matcher_to_apply.matches_w_trace(model)

    def _get_matcher(self, environment: InstructionApplicationEnvironment) -> StringMatcher:
        ie = environment.instruction
        matcher_sdv = symbol_lookup.lookup_string_matcher(ie.symbols, self.matcher_symbol_name)
        resolver = resolving_helper_for_instruction_env(environment.os_service, ie)
        return resolver.resolve_matcher(matcher_sdv)

    def _new_model(self, environment: InstructionEnvironmentForPostSdsStep) -> StringSource:
        the_model_constructor = model_constructor.of_str(self.put, self.actual_model_contents)
        return the_model_constructor(model_constructor.resolving_env_w_custom_dir_space(environment.sds))


ARBITRARY_SDV = string_matcher_sdv_constant_test_impl(MatcherWithConstantResult(True))

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
