import pathlib
import unittest
from abc import ABC

from exactly_lib.impls.instructions.multi_phase import change_dir as sut
from exactly_lib.tcfs.path_relativity import RelOptionType, RelSdsOptionType
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources.configuration import \
    ConfigurationBase, \
    suite_for_cases
from exactly_lib_test.impls.instructions.test_resources.assertion_utils.side_effects import AssertCwdIsSubDirOf
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt
from exactly_lib_test.tcfs.test_resources import sds_populator
from exactly_lib_test.test_resources.files.file_structure import DirContents, Dir, File
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


class Configuration(ConfigurationBase, ABC):
    def expect_successful_execution_with_side_effect(self,
                                                     side_effects_check: Assertion,
                                                     symbol_usages: Assertion = asrt.is_empty_sequence):
        raise NotImplementedError()

    def expect_target_is_not_a_directory(self):
        raise NotImplementedError()


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    return suite_for_cases(conf,
                           [
                               TestExistingDirectoryWithMultiplePathComponents,
                               TestArgumentExistsAsNonDirectory,
                               TestExistingDirectorySpecifiedRelativeSymbol,
                           ])


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
                            Dir.empty('second-component')
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
                    File.empty('file')
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
            '{relativity_option} existing-dir'.format(relativity_option=relativity_option.option_argument),
            self.conf.arrangement(
                sds_contents_before_main=relativity_option.populator_for_relativity_option_root__sds(
                    DirContents([Dir.empty('existing-dir')])),
                symbols=relativity_option.symbols.in_arrangement(),
            ),
            self.conf.expect_successful_execution_with_side_effect(
                AssertCwdIsSubDirOf(RelOptionType.REL_TMP,
                                    pathlib.Path('existing-dir')),
                symbol_usages=relativity_option.symbols.usages_expectation()
            )
        )
