import unittest

from exactly_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase, \
    suite_for_cases
from exactly_lib_test.test_resources.execution.eds_contents_check__va import act_dir_contains_exactly
from exactly_lib_test.test_resources.execution.eds_populator import act_dir_contents
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, Dir, empty_file
from exactly_lib_test.test_resources.parse import new_source2


class Configuration(ConfigurationBase):
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
                self.conf.expect_success_and_side_effects_on_files(
                        main_side_effects_on_files=act_dir_contains_exactly(DirContents([
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
    return suite_for_cases(conf,
                           [
                               TestCreationOfDirectory,
                               TestArgumentExistsAsNonDirectory,
                           ])
