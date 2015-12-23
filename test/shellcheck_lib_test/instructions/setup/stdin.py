import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.general.string import lines_content
from shellcheck_lib.instructions.setup import stdin as sut
from shellcheck_lib.instructions.utils import file_ref
from shellcheck_lib.test_case.help.instruction_description import Description
from shellcheck_lib.test_case.sections import common
from shellcheck_lib.test_case.sections.setup import SetupSettingsBuilder
from shellcheck_lib_test.instructions.setup.test_resources.instruction_check import Flow, TestCaseBase
from shellcheck_lib_test.instructions.setup.test_resources.settings_check import Assertion
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources.check_description import TestDescriptionBase
from shellcheck_lib_test.instructions.test_resources.utils import new_source, argument_list_source
from shellcheck_lib_test.util.file_structure import DirContents, empty_file, empty_dir


class TestParseSet(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        source = new_source('instruction-name', '')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_fail_when_there_is_more_than_three_argument(self):
        source = new_source('instruction-name', '--rel-home file superfluous-argument')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_succeed_when_syntax_is_correct__rel_home(self):
        source = new_source('instruction-name', '--rel-home file')
        sut.Parser().apply(source)

    def test_succeed_when_syntax_is_correct__rel_cwd(self):
        source = new_source('instruction-name', '--rel-cwd file')
        sut.Parser().apply(source)

    def test_succeed_when_syntax_is_correct__rel_tmp(self):
        source = new_source('instruction-name', '--rel-tmp file')
        sut.Parser().apply(source)

    def test_succeed_when_syntax_is_correct__rel_home__implicitly(self):
        source = new_source('instruction-name', 'file')
        sut.Parser().apply(source)

    def test_here_document(self):
        source = argument_list_source(['<<MARKER'],
                                      ['single line',
                                       'MARKER'])
        sut.Parser().apply(source)

    def test_fail_when_here_document_but_superfluous_arguments(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            source = argument_list_source(['<<MARKER', 'superfluous argument'],
                                          ['single line',
                                           'MARKER'])
            sut.Parser().apply(source)

    def test_file_name_can_be_quoted(self):
        source = new_source('instruction-name', '--rel-home "file name with space"')
        sut.Parser().apply(source)


class TestSuccessfulInstructionExecution(TestCaseBase):
    def test_file_rel_home__explicitly(self):
        self._check(
            Flow(sut.Parser(),
                 home_dir_contents=DirContents([
                     empty_file('file-in-home-dir.txt'),
                 ]),
                 expected_main_side_effects_on_environment=AssertStdinFileIsSetToFile(
                     file_ref.rel_home('file-in-home-dir.txt'))
                 ),
            new_source('instruction-name',
                       '--rel-home file-in-home-dir.txt'))

    def test_file_rel_home__implicitly(self):
        self._check(
            Flow(sut.Parser(),
                 home_dir_contents=DirContents([
                     empty_file('file-in-home-dir.txt'),
                 ]),
                 expected_main_side_effects_on_environment=AssertStdinFileIsSetToFile(
                     file_ref.rel_home('file-in-home-dir.txt')),
                 ),
            new_source('instruction-name',
                       'file-in-home-dir.txt'))


class TestFailingInstructionExecution(TestCaseBase):
    def test_referenced_file_does_not_exist(self):
        self._check(
            Flow(sut.Parser(),
                 expected_pre_validation_result=svh_check.is_validation_error(),
                 ),
            new_source('instruction-name',
                       '--rel-home non-existing-file'))

    def test_referenced_file_is_a_directory(self):
        self._check(
            Flow(sut.Parser(),
                 home_dir_contents=DirContents([
                     empty_dir('directory'),
                 ]),
                 expected_pre_validation_result=svh_check.is_validation_error(),
                 ),
            new_source('instruction-name',
                       '--rel-home directory'))

    def test_single_line_contents_from_here_document(self):
        self._check(
            Flow(sut.Parser(),
                 expected_main_side_effects_on_environment=AssertStdinIsSetToContents(
                     lines_content(['single line'])),
                 ),
            argument_list_source(['<<MARKER'],
                                 ['single line',
                                  'MARKER'])
        )


class AssertStdinFileIsSetToFile(Assertion):
    def __init__(self,
                 file_reference: file_ref.FileRef):
        self._file_reference = file_reference

    def apply(self,
              put: unittest.TestCase,
              environment: common.GlobalEnvironmentForPostEdsPhase,
              initial: SetupSettingsBuilder,
              actual_result: SetupSettingsBuilder):
        file_path = self._file_reference.file_path_pre_or_post_eds(environment.home_and_eds)
        put.assertIsNotNone(actual_result.stdin.file_name)
        put.assertEqual(str(file_path),
                        actual_result.stdin.file_name,
                        'Name of stdin file in Setup Settings')


class AssertStdinIsSetToContents(Assertion):
    def __init__(self,
                 contents: str):
        self._contents = contents

    def apply(self,
              put: unittest.TestCase,
              environment: common.GlobalEnvironmentForPostEdsPhase,
              initial: SetupSettingsBuilder,
              actual_result: SetupSettingsBuilder):
        put.assertIsNotNone(actual_result.stdin.contents)
        put.assertEqual(self._contents,
                        actual_result.stdin.contents,
                        'Contents of stdin in Setup Settings')


class TestDescription(TestDescriptionBase):
    def _description(self) -> Description:
        return sut.description('instruction name')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParseSet))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulInstructionExecution))
    ret_val.addTest(unittest.makeSuite(TestFailingInstructionExecution))
    ret_val.addTest(unittest.makeSuite(TestDescription))
    return ret_val


if __name__ == '__main__':
    unittest.main()
