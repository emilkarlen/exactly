import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException

from shellcheck_lib_test.instructions.setup.test_resources.instruction_check import Flow, TestCaseBase
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources.eds_contents_check import ActRootContainsExactly
from shellcheck_lib_test.instructions.test_resources.eds_populator import act_dir_contents
from shellcheck_lib_test.instructions.test_resources.utils import new_source
from shellcheck_lib_test.util.file_structure import DirContents, empty_dir, Dir, empty_file
from shellcheck_lib.instructions.setup import mkdir as sut


class TestParseSet(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        source = new_source('instruction-name', '')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_fail_when_superfluous_arguments(self):
        source = new_source('instruction-name', 'expected-argument superfluous-argument')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_success_when_correct_number_of_arguments(self):
        source = new_source('instruction-name', 'expected-argument')
        sut.Parser().apply(source)

    def test_success_when_correct_number_of_arguments__escaped(self):
        source = new_source('instruction-name', '"expected argument"')
        sut.Parser().apply(source)


class TestSuccessfulScenariosWithEmptyCwd(TestCaseBase):
    def test_creation_of_directory_with_single_path_component(self):
        self._check(
            Flow(sut.Parser(),
                 expected_main_side_effects_on_files=ActRootContainsExactly(DirContents([
                     empty_dir('dir-that-should-be-constructed')
                 ]))
                 ),
            new_source('instruction-name',
                       'dir-that-should-be-constructed'))

    def test_creation_of_directory_with_multiple_path_components(self):
        self._check(
            Flow(sut.Parser(),
                 expected_main_side_effects_on_files=ActRootContainsExactly(DirContents([
                     Dir('first-component', [
                         empty_dir('second-component')
                     ])
                 ]))
                 ),
            new_source('instruction-name',
                       'first-component/second-component'))


class TestSuccessfulScenariosWithExistingDirectories(TestCaseBase):
    def test_whole_argument_exists_as_directory__single_path_component(self):
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=act_dir_contents(DirContents([
                     empty_dir('existing-directory')
                 ])),
                 expected_main_side_effects_on_files=ActRootContainsExactly(DirContents([
                     empty_dir('existing-directory')
                 ]))
                 ),
            new_source('instruction-name',
                       'existing-directory'))

    def test_whole_argument_exists_as_directory__multiple_path_components(self):
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=act_dir_contents(DirContents([
                     Dir('first-component', [
                         empty_dir('second-component')
                     ])
                 ])),
                 expected_main_side_effects_on_files=ActRootContainsExactly(DirContents([
                     Dir('first-component', [
                         empty_dir('second-component')
                     ])
                 ]))
                 ),
            new_source('instruction-name',
                       'first-component/second-component'))

    def test_initial_component_of_argument_exists_as_directory__multiple_path_components(self):
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=act_dir_contents(DirContents([
                     Dir('first-component-that-exists', [
                         empty_dir('second-component')
                     ])
                 ])),
                 expected_main_side_effects_on_files=ActRootContainsExactly(DirContents([
                     Dir('first-component-that-exists', [
                         empty_dir('second-component')
                     ])
                 ]))
                 ),
            new_source('instruction-name',
                       'first-component-that-exists/second-component'))


class TestFailingScenarios(TestCaseBase):
    def test_argument_exists_as_non_directory__single_path_component(self):
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=act_dir_contents(DirContents([
                     empty_file('file')
                 ])),
                 expected_main_result=sh_check.IsHardError(),
                 ),
            new_source('instruction-name',
                       'file'))

    def test_argument_exists_as_non_directory__multiple_path_components(self):
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=act_dir_contents(DirContents([
                     Dir('existing-dir', [
                         empty_file('existing-file')
                     ])
                 ])),
                 expected_main_result=sh_check.IsHardError(),
                 ),
            new_source('instruction-name',
                       'existing-dir/existing-file'))

    def test_multi_path_component_with_middle_component_is_a_file(self):
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=act_dir_contents(DirContents([
                     Dir('existing-dir', [
                         empty_file('existing-file')
                     ])
                 ])),
                 expected_main_result=sh_check.IsHardError(),
                 ),
            new_source('instruction-name',
                       'existing-dir/existing-file/leaf-dir'))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParseSet))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulScenariosWithEmptyCwd))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulScenariosWithExistingDirectories))
    ret_val.addTest(unittest.makeSuite(TestFailingScenarios))
    return ret_val


if __name__ == '__main__':
    unittest.main()
