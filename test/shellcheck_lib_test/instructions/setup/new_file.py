import unittest

from shellcheck_lib.general.string import lines_content
from shellcheck_lib_test.instructions.setup.test_resources.instruction_check import Flow, TestCaseBase
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources.eds_contents_check import ActRootContainsExactly
from shellcheck_lib_test.instructions.test_resources.eds_populator import act_dir_contents
from shellcheck_lib_test.instructions.test_resources.utils import new_source, argument_list_source
from shellcheck_lib_test.util.file_structure import DirContents, empty_dir, Dir, empty_file, File
from shellcheck_lib.instructions.setup import new_file as sut


class TestCasesThatTestIntegrationByAFewRandomTests(TestCaseBase):
    def test_file_in_sub_dir__sub_dir_exists(self):
        self._check(
            Flow(
                sut.Parser(),
                eds_contents_before_main=act_dir_contents(DirContents([
                    empty_dir('existing-directory')
                ])),
                expected_main_side_effects_on_files=ActRootContainsExactly(DirContents([
                    Dir('existing-directory', [
                        empty_file('file-name.txt')])
                ]))),
            new_source('instruction-name',
                       'existing-directory/file-name.txt')
        )

    def test_single_line_contents(self):
        self._check(
            Flow(
                sut.Parser(),
                expected_main_side_effects_on_files=ActRootContainsExactly(DirContents([
                    File('file name',
                         lines_content(['single line']))
                ]))),
            argument_list_source(['file name', '<<MARKER'],
                                 ['single line',
                                  'MARKER'])
        )

    def test_argument_is_existing_file(self):
        self._check(
            Flow(
                sut.Parser(),
                expected_main_result=sh_check.IsHardError(),
                eds_contents_before_main=act_dir_contents(DirContents([
                    empty_file('existing-file')
                ])),
            ),
            new_source('instruction-name',
                       'existing-file')
        )


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCasesThatTestIntegrationByAFewRandomTests))
    return ret_val


if __name__ == '__main__':
    unittest.main()
