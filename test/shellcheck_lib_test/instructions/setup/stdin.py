import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException

from shellcheck_lib.instructions.utils import file_ref
from shellcheck_lib.test_case.sections.setup import SetupSettingsBuilder
from shellcheck_lib_test.instructions.setup.test_resources.instruction_check import Flow, TestCaseBase
from shellcheck_lib_test.instructions.setup.test_resources.settings_check import Assertion
from shellcheck_lib_test.instructions.test_resources.utils import new_source
from shellcheck_lib.test_case.sections import common
from shellcheck_lib_test.util.file_structure import DirContents, empty_file
from shellcheck_lib.instructions.setup import stdin as sut


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
                     file_ref.rel_home('file-in-home-dir.txt'))
                 ),
            new_source('instruction-name',
                       'file-in-home-dir.txt'))


class AssertStdinFileIsSetToFile(Assertion):
    def __init__(self,
                 file_reference: file_ref.FileRef):
        self._file_reference = file_reference

    def apply(self,
              put: unittest.TestCase,
              environment: common.GlobalEnvironmentForPostEdsPhase,
              initial: SetupSettingsBuilder,
              actual_result: SetupSettingsBuilder):
        file_path = self._file_reference.file_path(environment.home_and_eds)
        put.assertEqual(str(file_path),
                        actual_result.stdin_file_name,
                        'Name of stdin file in Setup Settings')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParseSet))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulInstructionExecution))
    return ret_val


if __name__ == '__main__':
    unittest.main()
