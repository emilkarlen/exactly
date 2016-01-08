import unittest

from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase
from shellcheck_lib_test.instructions.setup.test_resources.instruction_check import Expectation
from shellcheck_lib_test.instructions.test_resources.assertion_utils.side_effects import SideEffectsCheck
from shellcheck_lib_test.instructions.test_resources.eds_contents_check import ActRootContainsExactly
from shellcheck_lib_test.instructions.test_resources.eds_populator import act_dir_contents
from shellcheck_lib_test.instructions.test_resources.utils import new_source2
from shellcheck_lib_test.test_resources.file_structure import DirContents, empty_dir, Dir, empty_file


class Configuration(ConfigurationBase):
    def expect_successful_execution_with_side_effect(self,
                                                     side_effects_check: SideEffectsCheck):
        raise NotImplementedError()

    def expect_failure_to_create_dir(self):
        raise NotImplementedError()


class TestCaseBase(unittest.TestCase):
    def __init__(self, conf: Configuration):
        super().__init__()
        self.conf = conf


class TestCreationOfDirectory(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
                self,
                new_source2('first-component/second-component'),
                self.conf.empty_arrangement(),
                Expectation(main_side_effects_on_files=ActRootContainsExactly(DirContents([
                    Dir('first-component', [
                        empty_dir('second-component')
                    ])
                ])))
        )


class TestArgumentExistsAsNonDirectory(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
                self,
                new_source2('file'),
                self.conf.arrangement(eds_contents_before_main=act_dir_contents(DirContents([
                    empty_file('file')
                ]))),
                self.conf.expect_failure_to_create_dir()
        )


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    return unittest.TestSuite(
            tcc(conf) for tcc in [
                TestCreationOfDirectory,
                TestArgumentExistsAsNonDirectory,
            ])
