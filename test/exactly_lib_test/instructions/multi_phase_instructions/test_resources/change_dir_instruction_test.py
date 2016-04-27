import pathlib
import unittest

from exactly_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase, \
    suite_for_cases
from exactly_lib_test.instructions.test_resources.assertion_utils.side_effects__va import AssertCwdIsSubDirOfActDir
from exactly_lib_test.test_resources.execution.eds_populator import act_dir_contents
from exactly_lib_test.test_resources.file_structure import DirContents, Dir, empty_dir, empty_file
from exactly_lib_test.test_resources.parse import new_source2
from exactly_lib_test.test_resources.value_assertion import ValueAssertion


class Configuration(ConfigurationBase):
    def expect_successful_execution_with_side_effect(self,
                                                     side_effects_check: ValueAssertion):
        raise NotImplementedError()

    def expect_target_is_not_a_directory(self):
        raise NotImplementedError()


class TestCaseBase(unittest.TestCase):
    def __init__(self, conf: Configuration):
        super().__init__()
        self.conf = conf


class TestExistingDirectoryWithMultiplePathComponents(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
                self,
                new_source2('first-component/second-component'),
                self.conf.arrangement(
                        eds_contents_before_main=act_dir_contents(DirContents([
                            Dir('first-component', [
                                empty_dir('second-component')
                            ])]))),
                self.conf.expect_successful_execution_with_side_effect(
                        AssertCwdIsSubDirOfActDir(
                                pathlib.Path('first-component') / 'second-component')))


class TestArgumentExistsAsNonDirectory(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
                self,
                new_source2('file'),
                self.conf.arrangement(eds_contents_before_main=act_dir_contents(DirContents([
                    empty_file('file')
                ]))),
                self.conf.expect_target_is_not_a_directory())


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    return suite_for_cases(conf,
                           [
                               TestExistingDirectoryWithMultiplePathComponents,
                               TestArgumentExistsAsNonDirectory,
                           ])
