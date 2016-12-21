import unittest

from exactly_lib.instructions.multi_phase_instructions import new_dir as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.test_resources.execution import sds_test
from exactly_lib_test.test_resources.execution.sds_populator import act_dir_contents
from exactly_lib_test.test_resources.execution.sds_test import Arrangement, Expectation
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, Dir, empty_file
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.test_resources.value_assertions.sds_contents_check import act_dir_contains_exactly


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


class ParseAndMkDirAction(sds_test.Action):
    def __init__(self,
                 arguments: str):
        self.arguments = arguments

    def apply(self, sds: SandboxDirectoryStructure):
        directory_argument = sut.parse(self.arguments)
        return sut.make_dir_in_current_dir(directory_argument)


class TestCaseForCheckOfArgumentBase(sds_test.TestCaseBase):
    def _check_argument(self,
                        arguments: str,
                        arrangement: Arrangement,
                        expectation: Expectation):
        action = ParseAndMkDirAction(arguments)
        self._check(action,
                    arrangement,
                    expectation)


def is_success() -> va.ValueAssertion:
    return va.ValueIsNone()


def is_failure() -> va.ValueAssertion:
    return va.ValueIsNotNone()


class TestSuccessfulScenariosWithEmptyCwd(TestCaseForCheckOfArgumentBase):
    def test_creation_of_directory_with_single_path_component(self):
        self._check_argument('dir-that-should-be-constructed',
                             Arrangement(),
                             Expectation(expected_action_result=is_success(),
                                         expected_sds_contents_after=act_dir_contains_exactly(DirContents([
                                             empty_dir('dir-that-should-be-constructed')
                                         ]))
                                         ))

    def test_creation_of_directory_with_multiple_path_components(self):
        self._check_argument('first-component/second-component',
                             Arrangement(),
                             Expectation(expected_action_result=is_success(),
                                         expected_sds_contents_after=act_dir_contains_exactly(DirContents([
                                             Dir('first-component', [
                                                 empty_dir('second-component')
                                             ])
                                         ]))
                                         ))


class TestSuccessfulScenariosWithExistingDirectories(TestCaseForCheckOfArgumentBase):
    def test_whole_argument_exists_as_directory__single_path_component(self):
        self._check_argument('existing-directory',
                             Arrangement(sds_contents_before=act_dir_contents(DirContents([
                                 empty_dir('existing-directory')
                             ]))),
                             Expectation(
                                 expected_action_result=is_success(),
                                 expected_sds_contents_after=act_dir_contains_exactly(DirContents([
                                     empty_dir('existing-directory')
                                 ]))
                             ))

    def test_whole_argument_exists_as_directory__multiple_path_components(self):
        self._check_argument('first-component/second-component',
                             Arrangement(
                                 sds_contents_before=act_dir_contents(DirContents([
                                     Dir('first-component', [
                                         empty_dir('second-component')
                                     ])]))),
                             Expectation(
                                 expected_action_result=is_success(),
                                 expected_sds_contents_after=act_dir_contains_exactly(DirContents([
                                     Dir('first-component', [
                                         empty_dir('second-component')
                                     ])
                                 ]))
                             ))

    def test_initial_component_of_argument_exists_as_directory__multiple_path_components(self):
        self._check_argument('first-component-that-exists/second-component',
                             Arrangement(
                                 sds_contents_before=act_dir_contents(DirContents([
                                     Dir('first-component-that-exists', [
                                         empty_dir('second-component')])
                                 ]))),
                             Expectation(
                                 expected_action_result=is_success(),
                                 expected_sds_contents_after=act_dir_contains_exactly(DirContents([
                                     Dir('first-component-that-exists', [
                                         empty_dir('second-component')
                                     ])
                                 ]))
                             ))


class TestFailingScenarios(TestCaseForCheckOfArgumentBase):
    def test_argument_exists_as_non_directory__single_path_component(self):
        self._check_argument('file',
                             Arrangement(
                                 sds_contents_before=act_dir_contents(DirContents([
                                     empty_file('file')
                                 ]))),
                             Expectation(
                                 expected_action_result=is_failure(),
                             ))

    def test_argument_exists_as_non_directory__multiple_path_components(self):
        self._check_argument('existing-dir/existing-file',
                             Arrangement(
                                 sds_contents_before=act_dir_contents(DirContents([
                                     Dir('existing-dir', [
                                         empty_file('existing-file')
                                     ])
                                 ]))),
                             Expectation(
                                 expected_action_result=is_failure(),
                             ))

    def test_multi_path_component_with_middle_component_is_a_file(self):
        self._check_argument('existing-dir/existing-file/leaf-dir',
                             Arrangement(
                                 sds_contents_before=act_dir_contents(DirContents([
                                     Dir('existing-dir', [
                                         empty_file('existing-file')
                                     ])
                                 ]))),
                             Expectation(
                                 expected_action_result=is_failure(),
                             ))


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseSet),
        unittest.makeSuite(TestSuccessfulScenariosWithEmptyCwd),
        unittest.makeSuite(TestSuccessfulScenariosWithExistingDirectories),
        unittest.makeSuite(TestFailingScenarios),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
