import pathlib
import unittest

from exactly_lib.instructions.multi_phase_instructions import change_dir as sut
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelSdsOptionType
from exactly_lib_test.instructions.multi_phase_instructions.instruction_integration_test_resources.configuration import \
    ConfigurationBase, \
    suite_for_cases
from exactly_lib_test.instructions.test_resources.assertion_utils.side_effects import AssertCwdIsSubDirOf
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt
from exactly_lib_test.test_resources.file_structure import DirContents, Dir, empty_dir, empty_file
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class Configuration(ConfigurationBase):
    def expect_successful_execution_with_side_effect(self,
                                                     side_effects_check: asrt.ValueAssertion,
                                                     symbol_usages: asrt.ValueAssertion = asrt.is_empty_list):
        raise NotImplementedError()

    def expect_target_is_not_a_directory(self):
        raise NotImplementedError()


class TestCaseBase(unittest.TestCase):
    def __init__(self, conf: Configuration):
        super().__init__()
        self.conf = conf


class TestExistingDirectoryWithMultiplePathComponents(TestCaseBase):
    def runTest(self):
        self.conf.run_single_line_test_with_source_variants_and_source_check(
            self,
            'first-component/second-component',
            self.conf.arrangement(
                sds_contents_before_main=sds_populator.contents_in(
                    RelSdsOptionType.REL_ACT,
                    DirContents([
                        Dir('first-component', [
                            empty_dir('second-component')
                        ])]))),
            self.conf.expect_successful_execution_with_side_effect(
                AssertCwdIsSubDirOf(RelOptionType.REL_ACT,
                                    pathlib.Path('first-component') / 'second-component')))


class TestArgumentExistsAsNonDirectory(TestCaseBase):
    def runTest(self):
        self.conf.run_single_line_test_with_source_variants_and_source_check(
            self,
            'file',
            self.conf.arrangement(sds_contents_before_main=sds_populator.contents_in(
                RelSdsOptionType.REL_ACT,
                DirContents([
                    empty_file('file')
                ]))),
            self.conf.expect_target_is_not_a_directory())


class TestExistingDirectorySpecifiedRelativeSymbol(TestCaseBase):
    def runTest(self):
        relativity_option = rel_opt.symbol_conf_rel_sds(
            RelSdsOptionType.REL_TMP,
            'SYMBOL_NAME',
            sut.relativity_options(self.conf.phase_is_after_act()).options.accepted_relativity_variants)
        self.conf.run_single_line_test_with_source_variants_and_source_check(
            self,
            '{relativity_option} existing-dir'.format(relativity_option=relativity_option.option_string),
            self.conf.arrangement(
                sds_contents_before_main=relativity_option.populator_for_relativity_option_root__sds(
                    DirContents([empty_dir('existing-dir')])),
                symbols=relativity_option.symbols.in_arrangement(),
            ),
            self.conf.expect_successful_execution_with_side_effect(
                AssertCwdIsSubDirOf(RelOptionType.REL_TMP,
                                    pathlib.Path('existing-dir')),
                symbol_usages=relativity_option.symbols.usages_expectation()
            )
        )


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    return suite_for_cases(conf,
                           [
                               TestExistingDirectoryWithMultiplePathComponents,
                               TestArgumentExistsAsNonDirectory,
                               TestExistingDirectorySpecifiedRelativeSymbol,
                           ])
