import unittest
from typing import Callable, List

from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.instructions.multi_phase.copy.test_resources import argument_syntax as args
from exactly_lib_test.instructions.multi_phase.copy.test_resources import case_definitions
from exactly_lib_test.instructions.multi_phase.copy.test_resources import defs
from exactly_lib_test.instructions.multi_phase.instruction_integration_test_resources import \
    configuration as tc_configuration
from exactly_lib_test.instructions.multi_phase.instruction_integration_test_resources.configuration import \
    ConfigurationBase, TestCaseWithConfiguration
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.tcfs.test_resources.path_arguments import RelOptPathArgument
from exactly_lib_test.tcfs.test_resources.sds_check import sds_contents_check
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    syntax_and_relativities_cases = _syntax_and_relativities_cases(conf.phase_is_after_act())

    execution_cases = [
        TestValidationErrorWhenSrcRelHdsDoNotExist,
        TestHardErrorWhenSrcRelSdsDoNotExist,
        TestSuccessfulScenarioWithoutExplicitDestination,
        TestSuccessfulScenariosWithExplicitDestination,
        TestSuccessfulScenariosWithSymbolReferences,
    ]

    return tc_configuration.suite_for_cases(
        conf,
        syntax_and_relativities_cases +
        execution_cases
    )


def _syntax_and_relativities_cases(phase_if_after_act: bool) -> List[Callable[[ConfigurationBase], unittest.TestCase]]:
    phase_independent_case_constructors = [
        TestInvalidSyntax,
        TestIllegalRelativitiesIndependentOfPhase,
        TestLegalRelativitiesIndependentOfPhase,
        TestSuccessfulScenariosWithSymbolReferences,
    ]
    phase_dependent_case_constructors = (
        [
            TestLegalRelativitiesSpecificForPhasesAfterAct,
        ]
        if phase_if_after_act
        else
        [
            TestIllegalRelativitiesSpecificForPhasesBeforeAct,
        ]
    )

    return (
            phase_independent_case_constructors +
            phase_dependent_case_constructors
    )


class TestInvalidSyntax(TestCaseWithConfiguration):
    def runTest(self):
        for arguments_case in case_definitions.INVALI_SYNTAX_CASES:
            with self.subTest(arguments=arguments_case.name):
                self.conf.parse_checker.check_invalid_arguments(self, remaining_source(arguments_case.value))


class TestIllegalRelativitiesIndependentOfPhase(TestCaseWithConfiguration):
    def runTest(self):
        for illegal_case in case_definitions.illegal_relativities_independent_of_phase():
            with self.subTest(illegal_relativity=illegal_case.name):
                self.conf.parse_checker.check_invalid_arguments(self, illegal_case.value.as_remaining_source)


class TestIllegalRelativitiesSpecificForPhasesBeforeAct(TestCaseWithConfiguration):
    def runTest(self):
        for illegal_case in case_definitions.illegal_relativities_specific_for_phase_before_act():
            with self.subTest(illegal_dst=illegal_case.name):
                self.conf.parse_checker.check_invalid_arguments(self, illegal_case.value.as_remaining_source)


class TestLegalRelativitiesIndependentOfPhase(TestCaseWithConfiguration):
    def runTest(self):
        for relativity_case in case_definitions.legal_relativities_independent_of_phase():
            with self.subTest(relativities=relativity_case.name):
                self.conf.parse_checker.check_valid_arguments(self, relativity_case.value.as_remaining_source)


class TestLegalRelativitiesSpecificForPhasesAfterAct(TestCaseWithConfiguration):
    def runTest(self):
        for legal_case in case_definitions.legal_relativities_specific_for_phases_after_act():
            with self.subTest(legal_case.name):
                self.conf.parse_checker.check_valid_arguments(
                    self,
                    legal_case.value.as_remaining_source,
                )


class TestValidationErrorWhenSrcRelHdsDoNotExist(TestCaseWithConfiguration):
    def runTest(self):
        # ARRANGE #
        src_file_arg = RelOptPathArgument('non-existing-file', RelOptionType.REL_HDS_CASE)
        dst_file_arg = RelOptPathArgument('non-existing-file',
                                          defs.ARBITRARY_LEGAL_RELATIVITY__DST)
        arguments_cases = [
            NameAndValue(
                'without dst arg',
                args.copy(src_file_arg),
            ),
            NameAndValue(
                'with dst arg',
                args.copy(src_file_arg, dst_file_arg),
            ),
        ]
        for arguments_case in arguments_cases:
            with self.subTest(arguments_case.name):
                # ACT & ASSERT #
                self.conf.run_single_line_test_with_source_variants_and_source_check(
                    self,
                    arguments_case.value.as_str,
                    self.conf.arrangement(),
                    self.conf.expect_failing_validation_pre_sds()
                )


class TestHardErrorWhenSrcRelSdsDoNotExist(TestCaseWithConfiguration):
    def runTest(self):
        # ARRANGE #
        src_file_arg = RelOptPathArgument('non-existing-file', RelOptionType.REL_ACT)
        dst_file_arg = RelOptPathArgument('non-existing-file',
                                          defs.ARBITRARY_LEGAL_RELATIVITY__DST)
        arguments_cases = [
            NameAndValue(
                'without dst arg',
                args.copy(src_file_arg),
            ),
            NameAndValue(
                'with dst arg',
                args.copy(src_file_arg, dst_file_arg),
            ),
        ]
        for arguments_case in arguments_cases:
            with self.subTest(arguments_case.name):
                # ACT & ASSERT #
                self.conf.run_single_line_test_with_source_variants_and_source_check(
                    self,
                    arguments_case.value.as_str,
                    self.conf.arrangement(),
                    self.conf.expect_hard_error_of_main__any()
                )


class TestSuccessfulScenarioWithoutExplicitDestination(TestCaseWithConfiguration):
    def runTest(self):
        # ARRANGE #
        src_relativity_option = defs.DEFAULT_SRC_REL_OPT
        file_arg = src_relativity_option.path_argument_of_rel_name('existing-file')
        file_to_install = fs.DirContents([
            fs.File(file_arg.name, 'contents')
        ])
        # ACT & ASSERT #
        self.conf.run_single_line_test_with_source_variants_and_source_check(
            self,
            args.copy(file_arg).as_str,
            self.conf.arrangement(
                hds_contents=src_relativity_option.populator_for_relativity_option_root__hds(
                    file_to_install),
                symbols=src_relativity_option.symbols.in_arrangement(),
            ),
            self.conf.expect_success(
                main_side_effects_on_sds=sds_contents_check.cwd_contains_exactly(file_to_install),
                symbol_usages=src_relativity_option.symbols.usages_expectation(),
            )
        )


class TestSuccessfulScenariosWithExplicitDestination(TestCaseWithConfiguration):
    def runTest(self):
        # ARRANGE #
        dst_file_name = 'dst-file_name-file.txt'
        src_file = fs.File('src-file_name-file.txt', 'contents')
        home_dir_contents = fs.DirContents([src_file])
        expected_destination_dir_contents = fs.DirContents([fs.File(dst_file_name, src_file.contents)])

        src_rel_option = defs.ARBITRARY_SRC_REL_OPT
        dst_rel_option = defs.ARBITRARY_DST_REL_OPT
        # ACT & ASSERT #
        self.conf.run_test(
            self,
            args.copy(src_rel_option.path_argument_of_rel_name(src_file.name),
                      dst_rel_option.path_argument_of_rel_name(dst_file_name)
                      ).as_remaining_source,
            self.conf.arrangement(
                hds_contents=src_rel_option.populator_for_relativity_option_root__hds(home_dir_contents),
            ),
            self.conf.expect_success(
                main_side_effects_on_sds=sds_contents_check.non_hds_dir_contains_exactly(
                    dst_rel_option.root_dir__non_hds,
                    expected_destination_dir_contents),

            ),
        )


class TestSuccessfulScenariosWithSymbolReferences(TestCaseWithConfiguration):
    def runTest(self):
        # ARRANGE #
        dst_file_name = 'dst-file_name-file.txt'
        src_file = fs.File('src-file_name-file.txt', 'contents')
        home_dir_contents = fs.DirContents([src_file])
        expected_destination_dir_contents = fs.DirContents([fs.File(dst_file_name, src_file.contents)])

        src_rel_option = rel_opt_conf.symbol_conf_rel_hds(
            defs.ARBITRARY_LEGAL_RELATIVITY__SRC__HDS,
            'SRC_SYMBOL',
            defs.path_relativity_variants__src(self.conf.phase_is_after_act()),
        )
        dst_rel_option = rel_opt_conf.symbol_conf_rel_non_hds(
            defs.ARBITRARY_LEGAL_RELATIVITY__DST__NON_HDS,
            'DST_SYMBOL',
            defs.PATH_RELATIVITY_VARIANTS__DST,
        )
        # ACT & ASSERT #
        self.conf.run_test(
            self,
            args.copy(src_rel_option.path_argument_of_rel_name(src_file.name),
                      dst_rel_option.path_argument_of_rel_name(dst_file_name)
                      ).as_remaining_source,
            self.conf.arrangement(
                hds_contents=src_rel_option.populator_for_relativity_option_root__hds(home_dir_contents),
                symbols=SymbolContext.symbol_table_of_contexts(
                    src_rel_option.symbols.contexts_for_arrangement() +
                    dst_rel_option.symbols.contexts_for_arrangement()
                )
            ),
            self.conf.expect_success(
                symbol_usages=asrt.matches_sequence(
                    src_rel_option.symbols.usage_expectation_assertions() +
                    dst_rel_option.symbols.usage_expectation_assertions()
                ),
                main_side_effects_on_sds=sds_contents_check.non_hds_dir_contains_exactly(
                    dst_rel_option.root_dir__non_hds,
                    expected_destination_dir_contents),

            ),
        )
