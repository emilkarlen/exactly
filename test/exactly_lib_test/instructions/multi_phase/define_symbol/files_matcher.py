import unittest

from exactly_lib.instructions.multi_phase import define_symbol as sut
from exactly_lib.instructions.utils.logic_type_resolving_helper import resolving_helper_for_instruction_env
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol import lookups
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.files_matcher import models
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, FilesMatcher
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.multi_phase.define_symbol.test_case_base import TestCaseBaseForParser
from exactly_lib_test.instructions.multi_phase.define_symbol.test_resources import *
from exactly_lib_test.instructions.multi_phase.define_symbol.test_rsrcs import matcher_helpers
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage, sdv_assertions
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.files_matcher import files_matcher_stv_constant_test_impl, \
    is_reference_to_files_matcher__ref
from exactly_lib_test.symbol.test_resources.sdv_structure_assertions import matches_container
from exactly_lib_test.symbol.test_resources.symbol_syntax import NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case_utils.condition.integer.test_resources import arguments_building as int_args
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_syntax as fm_args
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as arg_syntax
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as fsm_args
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt_confs, matcher_assertions
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    expectation_type_config__non_is_success
from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_file
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
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

        argument_cases = [
            NameAndValue('value on same line',
                         '{files_matcher_type} {defined_name} = {matcher_argument}'
                         ),
            NameAndValue('value on following line',
                         '{files_matcher_type} {defined_name} = {new_line} {matcher_argument}'
                         ),
        ]

        for case in argument_cases:
            with self.subTest(case.name):
                source = single_line_source(
                    src(case.value,
                        defined_name=defined_name,
                        matcher_argument=arg_syntax.arbitrary_single_line_value_that_must_not_be_quoted()),
                )

                # EXPECTATION #

                expected_container = matches_container(
                    sdv_assertions.matches_sdtv_of_files_matcher()
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
                                         ARBITRARY_SDV)

        symbols = SymbolTable({
            referenced_symbol.name:
                symbol_utils.container(referenced_symbol.value)
        })

        # ARRANGE #

        source = single_line_source(
            src('{files_matcher_type} {defined_name} = {matcher_argument}',
                defined_name=defined_name,
                matcher_argument=referenced_symbol.name),
        )

        arrangement = ArrangementWithSds()

        # EXPECTATION #

        expected_container = matches_container(
            sdv_assertions.matches_sdtv_of_files_matcher(
                references=asrt.matches_sequence([
                    is_reference_to_files_matcher__ref(referenced_symbol.name)
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
        # ARRANGE #

        defined_name = 'defined_name'

        expected_container = matches_container(
            sdv_assertions.matches_sdtv_of_files_matcher()
        )

        not_num_files_beginning_with_a_eq_1_arg = self._not_num_files_beginning_with_a_eq_1_arg()

        cases = [
            NEA('should match',
                expected=matcher_assertions.is_matching_success(),
                actual=DirContents([
                    empty_file('a.x'),
                    empty_file('a.y'),
                    empty_file('b.x'),
                    empty_file('b.y'),
                ])
                ),
            NEA('should not match',
                expected=matcher_assertions.is_arbitrary_matching_failure(),
                actual=DirContents([
                    empty_file('a.x'),
                    empty_file('b.y'),
                    empty_file('b.x'),
                ])
                ),
        ]

        for case in cases:
            source = single_line_source(
                src('{files_matcher_type} {defined_name} = {matcher_argument}',
                    defined_name=defined_name,
                    matcher_argument=not_num_files_beginning_with_a_eq_1_arg),
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
                                                        actual_dir_contents=case.actual,
                                                        expected_matcher_result=case.expected),
            )

            with self.subTest(case.name):
                # ACT & ASSERT #
                self._check(source, ArrangementWithSds(), expectation)

    @staticmethod
    def _not_num_files_beginning_with_a_eq_1_arg() -> str:
        file_matcher_arg__begins_with_a = fm_args.file_matcher_arguments(
            name_pattern='a*'
        )

        files_matcher_args__num_files_eq_1 = fsm_args.NumFilesAssertionVariant(
            int_args.int_condition(comparators.EQ, 1)
        )

        args = fsm_args.SelectionAndMatcherArgumentsConstructor(
            file_matcher_arg__begins_with_a,
            files_matcher_args__num_files_eq_1,
        )

        return args.apply(
            expectation_type_config__non_is_success(ExpectationType.NEGATIVE)
        )


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
                    src('{files_matcher_type} {defined_name} = {matcher_argument}',
                        defined_name=defined_name,
                        matcher_argument=case.value),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    # ACT & ASSERT #
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


class AssertApplicationOfMatcherInSymbolTable(matcher_helpers.AssertApplicationOfMatcherInSymbolTable):
    def __init__(self,
                 matcher_symbol_name: str,
                 actual_dir_contents: DirContents,
                 expected_matcher_result: ValueAssertion[MatchingResult]):
        super().__init__(matcher_symbol_name,
                         expected_matcher_result)
        self.actual_dir_contents = actual_dir_contents

    def _apply_matcher(self,
                       environment: InstructionEnvironmentForPostSdsStep) -> MatchingResult:
        matcher_to_apply = self._get_matcher(environment)
        model = self._new_model(environment)
        return matcher_to_apply.matches_w_trace(model)

    def _get_matcher(self, environment: InstructionEnvironmentForPostSdsStep) -> FilesMatcher:
        sdv = lookups.lookup_files_matcher(environment.symbols, self.matcher_symbol_name)

        return resolving_helper_for_instruction_env(environment).resolve_files_matcher(sdv)

    def _new_model(self, environment: InstructionEnvironmentForPostSdsStep) -> FilesMatcherModel:
        rel_opt_conf = rel_opt_confs.conf_rel_sds(RelSdsOptionType.REL_RESULT)

        self._populate_root_dir(rel_opt_conf, environment)

        return models.non_recursive(
            rel_opt_conf.path_sdv_for_root_dir().resolve(environment.symbols)
                .value_of_any_dependency__d(environment.tcds),
        )

    def _populate_root_dir(self,
                           dir_conf: RelativityOptionConfiguration,
                           environment: InstructionEnvironmentForPostSdsStep):
        populator = dir_conf.populator_for_relativity_option_root(self.actual_dir_contents)
        populator.populate_tcds(environment.tcds)


ARBITRARY_SDV = files_matcher_stv_constant_test_impl(True,
                                                     references=[])

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
