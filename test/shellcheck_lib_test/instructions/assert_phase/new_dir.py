import unittest

from shellcheck_lib.instructions.assert_phase import new_dir as sut
from shellcheck_lib_test.instructions.assert_phase.test_resources.instruction_check import Flow, TestCaseBase
from shellcheck_lib_test.instructions.test_resources import pfh_check
from shellcheck_lib_test.instructions.test_resources.eds_contents_check import ActRootContainsExactly
from shellcheck_lib_test.instructions.test_resources.eds_populator import act_dir_contents
from shellcheck_lib_test.instructions.test_resources.utils import new_source
from shellcheck_lib_test.util.file_structure import DirContents, empty_dir, Dir, empty_file


class TestCasesThatTestIntegrationByAFewRandomTests(TestCaseBase):
    def test_creation_of_directory_with_multiple_path_components(self):
        self._chekk(
            Flow(sut.Parser(),
                 expected_main_side_effects_on_files=ActRootContainsExactly(DirContents([
                     Dir('first-component', [
                         empty_dir('second-component')
                     ])
                 ]))
                 ),
            new_source('instruction-name',
                       'first-component/second-component'))

    def test_argument_exists_as_non_directory__single_path_component(self):
        self._chekk(
            Flow(sut.Parser(),
                 eds_contents_before_main=act_dir_contents(DirContents([
                     empty_file('file')
                 ])),
                 expected_main_result=pfh_check.is_hard_error(),
                 ),
            new_source('instruction-name',
                       'file'))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCasesThatTestIntegrationByAFewRandomTests))
    return ret_val


if __name__ == '__main__':
    unittest.main()
