import pathlib
import unittest

from shellcheck_lib.test_case.sections.common import HomeAndEds
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase
from shellcheck_lib_test.instructions.test_resources.eds_populator import act_dir_contents
from shellcheck_lib_test.instructions.test_resources.utils import SideEffectsCheck, new_source2
from shellcheck_lib_test.test_resources.file_structure import DirContents, Dir, empty_dir, empty_file


class Configuration(ConfigurationBase):
    def expect_successful_execution_with_side_effect(self,
                                                     side_effects_check: SideEffectsCheck):
        raise NotImplementedError()

    def expectation_when_target_is_not_a_directory(self):
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
                        AssertCwdIsSubDirOfEds(
                                pathlib.Path('first-component') / 'second-component')))


class TestArgumentExistsAsNonDirectory(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
                self,
                new_source2('file'),
                self.conf.arrangement(eds_contents_before_main=act_dir_contents(DirContents([
                    empty_file('file')
                ]))),
                self.conf.expectation_when_target_is_not_a_directory())


class AssertCwdIsSubDirOfEds(SideEffectsCheck):
    def __init__(self, expected_sub_dir_of_eds: pathlib.PurePath):
        self.expected_sub_dir_of_eds = expected_sub_dir_of_eds

    def apply(self,
              put: unittest.TestCase,
              home_and_eds: HomeAndEds):
        put.assertEqual(home_and_eds.eds.act_dir / self.expected_sub_dir_of_eds,
                        pathlib.Path.cwd())


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    return unittest.TestSuite(
            tcc(conf) for tcc in [
                TestExistingDirectoryWithMultiplePathComponents,
                TestArgumentExistsAsNonDirectory,
            ])
