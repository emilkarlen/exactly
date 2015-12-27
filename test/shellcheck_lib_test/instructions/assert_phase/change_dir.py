import pathlib
import unittest

from shellcheck_lib.instructions.assert_phase import change_dir as sut
from shellcheck_lib_test.instructions.assert_phase.test_resources.instruction_check import Flow, TestCaseBase
from shellcheck_lib_test.instructions.multi_phase_instructions.change_dir import AssertCwdIsSubDirOfEds
from shellcheck_lib_test.instructions.test_resources import pfh_check
from shellcheck_lib_test.instructions.test_resources.eds_populator import act_dir_contents
from shellcheck_lib_test.instructions.test_resources.utils import new_source2
from shellcheck_lib_test.util.file_structure import DirContents, empty_dir, Dir, empty_file


class TestCasesThatTestIntegrationByAFewRandomTests(TestCaseBase):
    def test_creation_of_directory_with_multiple_path_components(self):
        self._chekk(
                Flow(sut.Parser(),
                     eds_contents_before_main=act_dir_contents(DirContents([
                         Dir('first-component', [
                             empty_dir('second-component')
                         ])])),
                     side_effects_check=AssertCwdIsSubDirOfEds(pathlib.Path('first-component') / 'second-component')
                     ),
                new_source2('first-component/second-component'))

    def test_argument_exists_as_non_directory__single_path_component(self):
        self._chekk(
                Flow(sut.Parser(),
                     eds_contents_before_main=act_dir_contents(DirContents([
                         empty_file('file')
                     ])),
                     expected_main_result=pfh_check.is_hard_error(),
                     ),
                new_source2('file'))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCasesThatTestIntegrationByAFewRandomTests))
    return ret_val


if __name__ == '__main__':
    unittest.main()
