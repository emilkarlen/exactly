import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from shellcheck_lib.instructions.cleanup import execute as sut
from shellcheck_lib.instructions.utils import relative_path_options as options
from shellcheck_lib_test.instructions.cleanup.test_resources.instruction_check import TestCaseBase, arrangement, \
    Expectation, is_success
from shellcheck_lib_test.instructions.test_resources import eds_populator
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources.execute_utils import source_for_interpreting
from shellcheck_lib_test.instructions.test_resources.utils import single_line_source
from shellcheck_lib_test.test_resources import python_program_execution as py_exe
from shellcheck_lib_test.test_resources.file_structure import DirContents, empty_file


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             source: SingleInstructionParserSource,
             arrangement: arrangement,
             expectation: Expectation):
        self._check(sut.parser('instruction-name'), source, arrangement, expectation)


class TestCasesThatTestIntegrationByAFewRandomTests(TestCaseBaseForParser):
    def test_successful_execution(self):
        self._run(single_line_source(py_exe.command_line_for_executing_program_via_command_line('exit(0)')),
                  arrangement(),
                  is_success(),
                  )

    def test_failing_execution(self):
        self._run(single_line_source(py_exe.command_line_for_executing_program_via_command_line('exit(1)')),
                  arrangement(),
                  Expectation(main_result=sh_check.IsHardError()),
                  )


class TestValidation(TestCaseBaseForParser):
    def test_failing_validation_of__rel_home_path(self):
        self._run(source_for_interpreting(options.REL_HOME_OPTION, 'non-existing-file.py'),
                  arrangement(),
                  Expectation(validate_pre_eds_result=svh_check.is_validation_error()),
                  )

    def test_failing_validation_by_main_of__rel_tmp_path(self):
        self._run(source_for_interpreting(options.REL_TMP_OPTION, 'non-existing-file.py'),
                  arrangement(),
                  Expectation(main_result=sh_check.IsHardError()),
                  )

    def test_successful_validation(self):
        self._run(source_for_interpreting(options.REL_TMP_OPTION, 'existing-file.py'),
                  arrangement(eds_contents_before_main=eds_populator.tmp_user_dir_contents(
                          DirContents([empty_file('existing-file.py')]))),
                  is_success(),
                  )


_NO_OPTION = ''


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCasesThatTestIntegrationByAFewRandomTests))
    ret_val.addTest(unittest.makeSuite(TestValidation))
    return ret_val


if __name__ == '__main__':
    unittest.main()
