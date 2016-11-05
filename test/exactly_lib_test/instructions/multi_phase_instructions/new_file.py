import unittest

from exactly_lib.instructions.multi_phase_instructions import new_file as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.string import lines_content
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.test_resources.execution import sds_test
from exactly_lib_test.test_resources.execution.eds_contents_check import ActRootContainsExactly, \
    TmpUserRootContainsExactly
from exactly_lib_test.test_resources.execution.eds_populator import act_dir_contents
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, Dir, empty_file, File
from exactly_lib_test.test_resources.parse import single_line_source, argument_list_source
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueIsNone, ValueIsNotNone


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


class ParseAndCreateFileAction(sds_test.Action):
    def __init__(self,
                 source: SingleInstructionParserSource):
        self.source = source

    def apply(self, eds: SandboxDirectoryStructure):
        file_info = sut.parse(self.source)
        return sut.create_file(file_info, eds)


class TestCaseBase(sds_test.TestCaseBase):
    def _test_argument(self,
                       source: SingleInstructionParserSource,
                       setup: sds_test.Check):
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
                            sds_test.Check(expected_action_result=is_success(),
                                           expected_eds_contents_after=ActRootContainsExactly(DirContents([
                                               empty_file('file-name.txt')
                                           ])),
                                           ))

    def test_file_in_sub_dir__sub_dir_exists(self):
        self._test_argument(single_line_source('existing-directory/file-name.txt'),
                            sds_test.Check(expected_action_result=is_success(),
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
                            sds_test.Check(expected_action_result=is_success(),
                                           expected_eds_contents_after=ActRootContainsExactly(DirContents([
                                               Dir('existing-directory', [
                                                   empty_file('file-name.txt')])
                                           ])),
                                           ))

    def test_file_in_sub_dir__sub_dir_does_not_exist__rel_tmp(self):
        self._test_argument(single_line_source('--rel-tmp existing-directory/file-name.txt'),
                            sds_test.Check(expected_action_result=is_success(),
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
                            sds_test.Check(expected_action_result=is_success(),
                                           expected_eds_contents_after=ActRootContainsExactly(DirContents([
                                               File('file-name.txt',
                                                    lines_content(['single line']))
                                           ])),
                                           ))


class TestFailingScenarios(TestCaseBase):
    def test_argument_is_existing_file(self):
        self._test_argument(single_line_source('existing-file'),
                            sds_test.Check(expected_action_result=is_failure(),
                                           eds_contents_before=act_dir_contents(DirContents([
                                               empty_file('existing-file')
                                           ])),
                                           ))

    def test_argument_is_under_path_that_contains_a_component_that_is_an_existing_file(self):
        self._test_argument(single_line_source('existing-directory/existing-file/directory/file-name.txt'),
                            sds_test.Check(expected_action_result=is_failure(),
                                           eds_contents_before=act_dir_contents(DirContents([
                                               Dir('existing-directory', [
                                                   empty_file('existing-file')
                                               ])
                                           ])),
                                           ))


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseWithNoContents),
        unittest.makeSuite(TestSuccessfulScenariosNoContent),
        unittest.makeSuite(TestSuccessfulScenariosWithContent),
        unittest.makeSuite(TestFailingScenarios),
        unittest.makeSuite(TestParseWithContents),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


if __name__ == '__main__':
    unittest.main()
