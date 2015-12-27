import pathlib
import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.general.string import lines_content
from shellcheck_lib.instructions.multi_phase_instructions import new_file as sut
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib.test_case.sections.common import HomeAndEds
from shellcheck_lib_test.instructions.test_resources.check_description import TestDescriptionBase
from shellcheck_lib_test.instructions.test_resources.eds_contents_check import ActRootContainsExactly, \
    TmpUserRootContainsExactly
from shellcheck_lib_test.instructions.test_resources.eds_populator import act_dir_contents
from shellcheck_lib_test.instructions.test_resources.utils import SideEffectsCheck, single_line_source, \
    argument_list_source
from shellcheck_lib_test.util import eds_test
from shellcheck_lib_test.util.file_structure import DirContents, empty_dir, Dir, empty_file, File
from shellcheck_lib_test.util.value_assertion import ValueAssertion, ValueIsNone, ValueIsNotNone


class AssertCwdIsSubDirOfEds(SideEffectsCheck):
    def __init__(self, expected_sub_dir_of_eds: pathlib.PurePath):
        self.expected_sub_dir_of_eds = expected_sub_dir_of_eds

    def apply(self,
              put: unittest.TestCase,
              home_and_eds: HomeAndEds):
        put.assertEqual(home_and_eds.eds.act_dir / self.expected_sub_dir_of_eds,
                        pathlib.Path.cwd())


class TestParseWithNoContents(unittest.TestCase):
    def test_path_is_mandatory__without_option(self):
        arguments = ''
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(single_line_source(arguments))

    def test_path_is_mandatory__with_option(self):
        arguments = '--rel-act'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(single_line_source(arguments))

    def test_when_no_option_path_should_be_relative_cwd(self):
        arguments = 'single-argument'
        actual = sut.parse(single_line_source(arguments))
        self.assertIs(sut.DestinationType.REL_CWD,
                      actual.destination_path.destination_type)
        self.assertEqual('single-argument',
                         str(actual.destination_path.path_argument))
        self.assertEqual('',
                         actual.contents)

    def test_fail_when_superfluous_arguments__without_option(self):
        arguments = 'expected-argument superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(single_line_source(arguments))

    def test_fail_when_superfluous_arguments__with_option(self):
        arguments = '--rel-act expected-argument superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(single_line_source(arguments))


class TestParseWithContents(unittest.TestCase):
    def test_fail_when_superfluous_arguments(self):
        source = argument_list_source(['file name', '<<MARKER', 'superfluous argument'],
                                      ['single line',
                                       'MARKER'])
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(source)

    def test_single_line(self):
        source = argument_list_source(['file name', '<<MARKER'],
                                      ['single line',
                                       'MARKER'])
        actual = sut.parse(source)
        self.assertIs(sut.DestinationType.REL_CWD,
                      actual.destination_path.destination_type)
        self.assertEqual('file name',
                         str(actual.destination_path.path_argument))
        self.assertEqual(lines_content(['single line']),
                         actual.contents)
        self.assertFalse(source.line_sequence.has_next())

    def test_single_line__with_option(self):
        source = argument_list_source(['--rel-tmp', 'file name', '<<MARKER'],
                                      ['single line',
                                       'MARKER',
                                       'following line'])
        actual = sut.parse(source)
        self.assertIs(sut.DestinationType.REL_TMP_DIR,
                      actual.destination_path.destination_type)
        self.assertEqual('file name',
                         str(actual.destination_path.path_argument))
        self.assertEqual(lines_content(['single line']),
                         actual.contents)
        self.assertTrue(source.line_sequence.has_next())
        self.assertEqual('following line',
                         source.line_sequence.next_line())


class ParseAndCreateFileAction(eds_test.Action):
    def __init__(self,
                 source: SingleInstructionParserSource):
        self.source = source

    def apply(self, eds: ExecutionDirectoryStructure):
        file_info = sut.parse(self.source)
        return sut.create_file(file_info, eds)


class TestCaseBase(eds_test.TestCaseBase):
    def _test_argument(self,
                       source: SingleInstructionParserSource,
                       setup: eds_test.Check):
        action = ParseAndCreateFileAction(source)
        self._check_action(action,
                           setup)


def is_success() -> ValueAssertion:
    return ValueIsNone()


def is_failure() -> ValueAssertion:
    return ValueIsNotNone()


class TestSuccessfulScenariosNoContent(TestCaseBase):
    def test_file_relative_pwd(self):
        self._test_argument(single_line_source('file-name.txt'),
                            eds_test.Check(expected_action_result=is_success(),
                                           expected_eds_contents_after=ActRootContainsExactly(DirContents([
                                               empty_file('file-name.txt')
                                           ])),
                                           ))

    def test_file_in_sub_dir__sub_dir_exists(self):
        self._test_argument(single_line_source('existing-directory/file-name.txt'),
                            eds_test.Check(expected_action_result=is_success(),
                                           eds_contents_before=act_dir_contents(DirContents([
                                               empty_dir('existing-directory')
                                           ])),
                                           expected_eds_contents_after=ActRootContainsExactly(DirContents([
                                               Dir('existing-directory', [
                                                   empty_file('file-name.txt')])
                                           ])),
                                           ))

    def test_file_in_sub_dir__sub_dir_does_not_exist(self):
        self._test_argument(single_line_source('existing-directory/file-name.txt'),
                            eds_test.Check(expected_action_result=is_success(),
                                           expected_eds_contents_after=ActRootContainsExactly(DirContents([
                                               Dir('existing-directory', [
                                                   empty_file('file-name.txt')])
                                           ])),
                                           ))

    def test_file_in_sub_dir__sub_dir_does_not_exist__rel_tmp(self):
        self._test_argument(single_line_source('--rel-tmp existing-directory/file-name.txt'),
                            eds_test.Check(expected_action_result=is_success(),
                                           expected_eds_contents_after=TmpUserRootContainsExactly(DirContents([
                                               Dir('existing-directory', [
                                                   empty_file('file-name.txt')])
                                           ])),
                                           ))


class TestSuccessfulScenariosWithContent(TestCaseBase):
    def test_file_relative_pwd(self):
        source = argument_list_source(['file-name.txt', '<<MARKER'],
                                      ['single line',
                                       'MARKER'])
        self._test_argument(source,
                            eds_test.Check(expected_action_result=is_success(),
                                           expected_eds_contents_after=ActRootContainsExactly(DirContents([
                                               File('file-name.txt',
                                                    lines_content(['single line']))
                                           ])),
                                           ))


class TestFailingScenarios(TestCaseBase):
    def test_argument_is_existing_file(self):
        self._test_argument(single_line_source('existing-file'),
                            eds_test.Check(expected_action_result=is_failure(),
                                           eds_contents_before=act_dir_contents(DirContents([
                                               empty_file('existing-file')
                                           ])),
                                           ))

    def test_argument_is_under_path_that_contains_a_component_that_is_an_existing_file(self):
        self._test_argument(single_line_source('existing-directory/existing-file/directory/file-name.txt'),
                            eds_test.Check(expected_action_result=is_failure(),
                                           eds_contents_before=act_dir_contents(DirContents([
                                               Dir('existing-directory', [
                                                   empty_file('existing-file')
                                               ])
                                           ])),
                                           ))


class TestDescription(TestDescriptionBase):
    def _description(self) -> Description:
        return sut.TheDescription('instruction name')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParseWithNoContents))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulScenariosNoContent))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulScenariosWithContent))
    ret_val.addTest(unittest.makeSuite(TestFailingScenarios))
    ret_val.addTest(unittest.makeSuite(TestParseWithContents))
    ret_val.addTest(unittest.makeSuite(TestDescription))
    return ret_val


if __name__ == '__main__':
    unittest.main()
