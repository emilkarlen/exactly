import unittest
from abc import ABC

from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_documentation_instance
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources.configuration import \
    ConfigurationBase
from exactly_lib_test.impls.instructions.multi_phase.new_dir import explicit_contents
from exactly_lib_test.impls.instructions.multi_phase.new_dir.test_resources import path_config
from exactly_lib_test.impls.instructions.multi_phase.new_dir.test_resources.abstract_syntax import NewDirArguments
from exactly_lib_test.impls.types.files_source.test_resources import abstract_syntaxes as fs_abs_stx
from exactly_lib_test.impls.types.test_resources.relativity_options import \
    RelativityOptionConfigurationForRelNonHds
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources.dir_populator import NonHdsPopulator
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import Dir
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    TcdsActionFromSdsAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.files_source.test_resources import validation_cases


class Configuration(ConfigurationBase, ABC):
    def expect_failure_to_create_dir(self,
                                     symbol_usages: Assertion = asrt.is_empty_sequence):
        raise NotImplementedError()


def suite_for(conf: Configuration) -> unittest.TestSuite:
    test_cases = [
        TestCreationOfDirectory,
        TestArgumentExistsAsNonDirectory,
        TestFailingValidationOfContents,
        TestSuccessfulWithExplicitContents,
    ]
    suites = [
        tc(conf)
        for tc in test_cases
    ]
    suites.append(suite_for_documentation_instance(conf.documentation()))
    return unittest.TestSuite(suites)


class TestCaseBase(unittest.TestCase):
    def __init__(self, conf: Configuration):
        super().__init__()
        self.conf = conf

    def _arrangement_with_cwd_as_non_of_the_relativity_root_dirs(
            self,
            rel_opt_conf: RelativityOptionConfigurationForRelNonHds,
            sds_contents_before_main: NonHdsPopulator = NonHdsPopulator.empty(),
    ):
        return self.conf.arrangement(
            tcds_contents=sds_contents_before_main,
            pre_contents_population_action=TcdsActionFromSdsAction(
                path_config.SETUP_CWD_ACTION),
            symbols=rel_opt_conf.symbols.in_arrangement())

    def _test_relativity(self,
                         rel_opt_conf: RelativityOptionConfigurationForRelNonHds,
                         ):
        raise NotImplementedError('abstract method')

    def shortDescription(self):
        return '{}\n / {}'.format(type(self), type(self.conf))

    def runTest(self):
        for rel_opt_conf in path_config.RELATIVITY_OPTIONS__PHASE_INTEGRATION:
            with self.subTest(relativity=rel_opt_conf.name):
                self._test_relativity(rel_opt_conf)


class TestCreationOfDirectory(TestCaseBase):
    def _test_relativity(self,
                         rel_opt_conf: RelativityOptionConfigurationForRelNonHds,
                         ):
        top_dir__name = 'top-dir'
        sub_dir__name = 'sub-dir'
        instruction_syntax = NewDirArguments.implicitly_empty(
            rel_opt_conf.path_abs_stx_of_name__c([
                top_dir__name,
                sub_dir__name,
            ])
        )
        self.conf.instruction_checker.check_parsing__abs_stx__const(
            self,
            self.conf.parser(),
            instruction_syntax,
            self._arrangement_with_cwd_as_non_of_the_relativity_root_dirs(rel_opt_conf),
            self.conf.expect_success(
                main_side_effects_on_sds=rel_opt_conf.assert_root_dir_contains_exactly__p([
                    Dir(top_dir__name, [
                        Dir.empty(sub_dir__name)
                    ])
                ]),
                symbol_usages=rel_opt_conf.symbols.usages_expectation(),
            )
        )


class TestArgumentExistsAsNonDirectory(TestCaseBase):
    def _test_relativity(self,
                         rel_opt_conf: RelativityOptionConfigurationForRelNonHds,
                         ):
        existing_regular_file = fs.File.empty('a-regular-file')
        instruction_syntax = NewDirArguments.implicitly_empty(
            rel_opt_conf.path_abs_stx_of_name(existing_regular_file.name)
        )
        self.conf.instruction_checker.check_parsing__abs_stx__const(
            self,
            self.conf.parser(),
            instruction_syntax,
            self._arrangement_with_cwd_as_non_of_the_relativity_root_dirs(
                rel_opt_conf,
                sds_contents_before_main=rel_opt_conf.populator_for_relativity_option_root__non_hds__s([
                    existing_regular_file
                ])),
            self.conf.expect_failure_to_create_dir(
                symbol_usages=rel_opt_conf.symbols.usages_expectation(),
            )
        )


class TestFailingValidationOfContents(TestCaseBase):
    def _test_relativity(self,
                         rel_opt_conf: RelativityOptionConfigurationForRelNonHds,
                         ):
        # ARRANGE #
        dst_path = rel_opt_conf.path_abs_stx_of_name('non-existing-file')
        for modification in fs_abs_stx.ModificationType:
            for validation_case in validation_cases.failing_validation_cases():
                instruction_syntax = NewDirArguments(
                    dst_path,
                    fs_abs_stx.DirContentsExplicitAbsStx(modification,
                                                         validation_case.value.syntax),
                )
                all_symbols = rel_opt_conf.symbols.contexts_for_arrangement() + [validation_case.value.symbol_context]
                # ACT & ASSERT
                self.conf.instruction_checker.check_parsing__abs_stx__const(
                    self,
                    self.conf.parser(),
                    instruction_syntax,
                    self.conf.arrangement(
                        symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
                    ),
                    self.conf.expect_failing_validation(
                        validation_case.value.actual,
                        symbol_usages=SymbolContext.usages_assertion_of_contexts(all_symbols),
                    )
                )


class TestSuccessfulWithExplicitContents(TestCaseBase):
    def _test_relativity(self,
                         rel_opt_conf: RelativityOptionConfigurationForRelNonHds,
                         ):
        # ARRANGE #
        for case in explicit_contents.successful_cases():
            dst_path = rel_opt_conf.path_abs_stx_of_name(case.dst_file_name)
            instruction_syntax = NewDirArguments(
                dst_path,
                case.contents_syntax,
            )
            # ACT & ASSERT
            self.conf.instruction_checker.check_parsing__abs_stx__const(
                self,
                self.conf.parser(),
                instruction_syntax,
                self.conf.arrangement(
                    symbols=rel_opt_conf.symbols.in_arrangement(),
                    tcds_contents=rel_opt_conf.populator_for_relativity_option_root__non_hds__s(
                        case.pre_existing_files
                    ),
                ),
                self.conf.expect_success(
                    main_side_effects_on_sds=rel_opt_conf.assert_root_dir_contains_exactly__p(
                        case.expected_files,
                    ),
                    symbol_usages=rel_opt_conf.symbols.usages_expectation(),
                )
            )
