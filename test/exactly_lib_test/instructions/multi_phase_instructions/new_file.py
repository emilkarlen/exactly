import unittest

from exactly_lib.instructions.multi_phase_instructions import new_file as sut
from exactly_lib.instructions.utils.relativity_root import RelOptionType
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.string import lines_content
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.utils.arg_parse.test_resources import args_with_rel_ops
from exactly_lib_test.test_resources.execution.sds_check import sds_test
from exactly_lib_test.test_resources.execution.sds_check import sds_utils
from exactly_lib_test.test_resources.execution.sds_check.sds_contents_check import act_dir_contains_exactly, \
    tmp_user_dir_contains_exactly
from exactly_lib_test.test_resources.execution.sds_check.sds_populator import act_dir_contents
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, Dir, empty_file, File
from exactly_lib_test.test_resources.parse import argument_list_source, single_line_source
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

    def test_rel_result_option_is_not_allowed(self):
        arguments = args_with_rel_ops('{rel_result_option} file')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(single_line_source(arguments))

    def test_when_no_option_path_should_be_relative_cwd(self):
        arguments = 'single-argument'
        actual = sut.parse(single_line_source(arguments))
        self.assertIs(RelOptionType.REL_CWD,
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
        self.assertIs(RelOptionType.REL_CWD,
                      actual.destination_path.destination_type)
        self.assertEqual('file name',
                         str(actual.destination_path.path_argument))
        self.assertEqual(lines_content(['single line']),
                         actual.contents)
        self.assertFalse(source.has_current_line)

    def test_single_line__with_option(self):
        source = argument_list_source(['--rel-tmp', 'file name', '<<MARKER'],
                                      ['single line',
                                       'MARKER',
                                       'following line'])
        actual = sut.parse(source)
        self.assertIs(RelOptionType.REL_TMP,
                      actual.destination_path.destination_type)
        self.assertEqual('file name',
                         str(actual.destination_path.path_argument))
        self.assertEqual(lines_content(['single line']),
                         actual.contents)
        self.assertTrue(source.has_current_line)
        self.assertEqual('following line',
                         source.current_line_text)


class ParseAndCreateFileAction(sds_utils.SdsAction):
    def __init__(self,
                 source: ParseSource):
        self.source = source

    def apply(self, sds: SandboxDirectoryStructure):
        file_info = sut.parse(self.source)
        return sut.create_file(file_info, sds)


class TestCaseBase(sds_test.TestCaseBase):
    def _check_argument(self,
                        source: ParseSource,
                        arrangement: sds_test.Arrangement,
                        expectation: sds_test.Expectation):
        action = ParseAndCreateFileAction(source)
        self._check(action,
                    arrangement,
                    expectation)


def is_success() -> ValueAssertion:
    return ValueIsNone()


def is_failure() -> ValueAssertion:
    return ValueIsNotNone()


class TestSuccessfulScenariosNoContent(TestCaseBase):
    def test_file_relative_cwd(self):
        self._check_argument(single_line_source('file-name.txt'),
                             sds_test.Arrangement(),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  expected_sds_contents_after=act_dir_contains_exactly(DirContents([
                                                      empty_file('file-name.txt')
                                                  ])),
                                                  ))

    def test_file_in_sub_dir__sub_dir_exists(self):
        self._check_argument(single_line_source('existing-directory/file-name.txt'),
                             sds_test.Arrangement(sds_contents_before=act_dir_contents(DirContents([
                                 empty_dir('existing-directory')
                             ]))),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  expected_sds_contents_after=act_dir_contains_exactly(DirContents([
                                                      Dir('existing-directory', [
                                                          empty_file('file-name.txt')])
                                                  ])),
                                                  ))

    def test_file_in_sub_dir__sub_dir_does_not_exist(self):
        self._check_argument(single_line_source('existing-directory/file-name.txt'),
                             sds_test.Arrangement(),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  expected_sds_contents_after=act_dir_contains_exactly(DirContents([
                                                      Dir('existing-directory', [
                                                          empty_file('file-name.txt')])
                                                  ])),
                                                  ))

    def test_file_in_sub_dir__sub_dir_does_not_exist__rel_tmp(self):
        self._check_argument(single_line_source('--rel-tmp existing-directory/file-name.txt'),
                             sds_test.Arrangement(),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  expected_sds_contents_after=tmp_user_dir_contains_exactly(
                                                      DirContents([
                                                          Dir('existing-directory', [
                                                              empty_file('file-name.txt')])
                                                      ])),
                                                  ))


class TestSuccessfulScenariosWithContent(TestCaseBase):
    def test_file_relative_cwd(self):
        source = argument_list_source(['file-name.txt', '<<MARKER'],
                                      ['single line',
                                       'MARKER'])
        self._check_argument(source,
                             sds_test.Arrangement(),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  expected_sds_contents_after=act_dir_contains_exactly(DirContents([
                                                      File('file-name.txt',
                                                           lines_content(['single line']))
                                                  ])),
                                                  ))


class TestFailingScenarios(TestCaseBase):
    def test_argument_is_existing_file(self):
        self._check_argument(single_line_source('existing-file'),
                             sds_test.Arrangement(
                                 sds_contents_before=act_dir_contents(DirContents([
                                     empty_file('existing-file')
                                 ]))),
                             sds_test.Expectation(expected_action_result=is_failure(),
                                                  ))

    def test_argument_is_under_path_that_contains_a_component_that_is_an_existing_file(self):
        self._check_argument(single_line_source('existing-directory/existing-file/directory/file-name.txt'),
                             sds_test.Arrangement(sds_contents_before=act_dir_contents(DirContents([
                                 Dir('existing-directory', [
                                     empty_file('existing-file')
                                 ])
                             ]))),
                             sds_test.Expectation(expected_action_result=is_failure(),
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
    unittest.TextTestRunner().run(suite())
