import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.multi_phase_instructions import new_dir as sut
from shellcheck_lib.test_case.help.instruction_description import Description
from shellcheck_lib_test.instructions.test_resources.check_description import TestDescriptionBase
from shellcheck_lib_test.util import tmp_dir_test
from shellcheck_lib_test.util.file_checks import dir_contains_exactly
from shellcheck_lib_test.util.file_structure import DirContents, empty_dir, Dir, empty_file
from shellcheck_lib_test.util.tmp_dir_test import Check
from shellcheck_lib_test.util.value_assertion import ValueAssertion, ValueIsNone, ValueIsNotNone


class TestParseSet(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        arguments = ''
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(arguments)

    def test_fail_when_superfluous_arguments(self):
        arguments = 'expected-argument superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(arguments)

    def test_strip_trailing_space(self):
        arguments = '  expected-argument  '
        result = sut.parse(arguments)
        self.assertEqual('expected-argument',
                         result)

    def test_success_when_correct_number_of_arguments(self):
        arguments = 'expected-argument'
        result = sut.parse(arguments)
        self.assertEqual('expected-argument',
                         result)

    def test_success_when_correct_number_of_arguments__escaped(self):
        arguments = '"expected argument"'
        result = sut.parse(arguments)
        self.assertEqual('expected argument',
                         result)


class ParseAndMkDirAction:
    def __init__(self,
                 arguments: str):
        self.arguments = arguments

    def __call__(self, *args, **kwargs):
        directory_argument = sut.parse(self.arguments)
        return sut.make_dir_in_current_dir(directory_argument)


class TestCaseBase2(tmp_dir_test.TestCaseBase):
    def _test_argument(self,
                       arguments: str,
                       setup: tmp_dir_test.Check):
        action = ParseAndMkDirAction(arguments)
        self._check_action(action,
                           setup)


def is_success() -> ValueAssertion:
    return ValueIsNone()


def is_failure() -> ValueAssertion:
    return ValueIsNotNone()


class TestSuccessfulScenariosWithEmptyCwd(TestCaseBase2):
    def test_creation_of_directory_with_single_path_component(self):
        self._test_argument('dir-that-should-be-constructed',
                            Check(expected_action_result=is_success(),
                                  expected_dir_contents_after=dir_contains_exactly(DirContents([
                                      empty_dir('dir-that-should-be-constructed')
                                  ]))
                                  ))

    def test_creation_of_directory_with_multiple_path_components(self):
        self._test_argument('first-component/second-component',
                            Check(expected_action_result=is_success(),
                                  expected_dir_contents_after=dir_contains_exactly(DirContents([
                                      Dir('first-component', [
                                          empty_dir('second-component')
                                      ])
                                  ]))
                                  ))


class TestSuccessfulScenariosWithExistingDirectories(TestCaseBase2):
    def test_whole_argument_exists_as_directory__single_path_component(self):
        self._test_argument('existing-directory',
                            Check(
                                dir_contents_before=DirContents([
                                    empty_dir('existing-directory')
                                ]),
                                expected_action_result=is_success(),
                                expected_dir_contents_after=dir_contains_exactly(DirContents([
                                    empty_dir('existing-directory')
                                ]))
                            ))

    def test_whole_argument_exists_as_directory__multiple_path_components(self):
        self._test_argument('first-component/second-component',
                            Check(
                                dir_contents_before=DirContents([
                                    Dir('first-component', [
                                        empty_dir('second-component')
                                    ])]),
                                expected_action_result=is_success(),

                                expected_dir_contents_after=dir_contains_exactly(DirContents([
                                    Dir('first-component', [
                                        empty_dir('second-component')
                                    ])
                                ]))
                            ))

    def test_initial_component_of_argument_exists_as_directory__multiple_path_components(self):
        self._test_argument('first-component-that-exists/second-component',
                            Check(
                                dir_contents_before=DirContents([
                                    Dir('first-component-that-exists', [
                                        empty_dir('second-component')])
                                ]),
                                expected_action_result=is_success(),
                                expected_dir_contents_after=dir_contains_exactly(DirContents([
                                    Dir('first-component-that-exists', [
                                        empty_dir('second-component')
                                    ])
                                ]))
                            ))


class TestFailingScenarios(TestCaseBase2):
    def test_argument_exists_as_non_directory__single_path_component(self):
        self._test_argument('file',
                            Check(
                                dir_contents_before=DirContents([
                                    empty_file('file')
                                ]),
                                expected_action_result=is_failure(),
                            ))

    def test_argument_exists_as_non_directory__multiple_path_components(self):
        self._test_argument('existing-dir/existing-file',
                            Check(
                                dir_contents_before=DirContents([
                                    Dir('existing-dir', [
                                        empty_file('existing-file')
                                    ])
                                ]),
                                expected_action_result=is_failure(),
                            ))

    def test_multi_path_component_with_middle_component_is_a_file(self):
        self._test_argument('existing-dir/existing-file/leaf-dir',
                            Check(
                                dir_contents_before=DirContents([
                                    Dir('existing-dir', [
                                        empty_file('existing-file')
                                    ])
                                ]),
                                expected_action_result=is_failure(),
                            ))


class TestDescription(TestDescriptionBase):
    def _description(self) -> Description:
        return sut.description('instruction name')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParseSet))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulScenariosWithEmptyCwd))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulScenariosWithExistingDirectories))
    ret_val.addTest(unittest.makeSuite(TestFailingScenarios))
    ret_val.addTest(unittest.makeSuite(TestDescription))
    return ret_val


if __name__ == '__main__':
    unittest.main()
