import pathlib
import unittest

from exactly_lib.instructions.multi_phase_instructions import change_dir as sut
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase, \
    suite_for_cases
from exactly_lib_test.instructions.test_resources.assertion_utils.side_effects import AssertCwdIsSubDirOf
from exactly_lib_test.instructions.test_resources.relativity_options import SymbolsRelativityHelper
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
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
                sds_contents_before_main=sds_populator.act_dir_contents(
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
            self.conf.arrangement(sds_contents_before_main=sds_populator.act_dir_contents(
                DirContents([
                    empty_file('file')
                ]))),
            self.conf.expect_target_is_not_a_directory())


class TestExistingDirectorySpecifiedRelativeSymbol(TestCaseBase):
    def runTest(self):
        symbols_helper = SymbolsRelativityHelper(
            RelOptionType.REL_TMP,
            sut.relativity_options(self.conf.phase_is_after_act()).options.accepted_relativity_variants,
            'SYMBOL_NAME',
        )
        self.conf.run_single_line_test_with_source_variants_and_source_check(
            self,
            '--rel SYMBOL_NAME existing-dir',
            self.conf.arrangement(
                sds_contents_before_main=sds_populator.rel_symbol(
                    RelOptionType.REL_TMP,
                    DirContents([empty_dir('existing-dir')])),
                symbols=symbols_helper.symbols_in_arrangement(),
            ),
            self.conf.expect_successful_execution_with_side_effect(
                AssertCwdIsSubDirOf(RelOptionType.REL_TMP,
                                    pathlib.Path('existing-dir')),
                symbol_usages=symbols_helper.symbol_usage_expectation()
            )
        )


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    return suite_for_cases(conf,
                           [
                               TestExistingDirectoryWithMultiplePathComponents,
                               TestArgumentExistsAsNonDirectory,
                               TestExistingDirectorySpecifiedRelativeSymbol,
                           ])
