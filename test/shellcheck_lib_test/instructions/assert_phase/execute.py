import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from shellcheck_lib.instructions.assert_phase import execute as sut
from shellcheck_lib.instructions.utils import relative_path_options as options
from shellcheck_lib_test.instructions.assert_phase.test_resources.instruction_check import TestCaseBase, \
    Arrangement, Expectation, is_pass
from shellcheck_lib_test.instructions.test_resources import eds_populator
from shellcheck_lib_test.instructions.test_resources import pfh_check
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources.execute_utils import source_for_interpreting
from shellcheck_lib_test.instructions.test_resources.utils import single_line_source
from shellcheck_lib_test.test_resources import python_program_execution as py_exe
from shellcheck_lib_test.test_resources.file_structure import DirContents, empty_file


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             source: SingleInstructionParserSource,
             arrangement: Arrangement,
             expectation: Expectation):
        self._check(sut.parser('instruction-name'), source, arrangement, expectation)


class TestCasesThatTestIntegrationByAFewRandomTests(TestCaseBaseForParser):
    def test_successful_execution(self):
        self._run(single_line_source(py_exe.command_line_for_executing_program_via_command_line('exit(0)')),
                  Arrangement(),
                  is_pass(),
                  )

    def test_failing_execution(self):
        self._run(
                single_line_source(py_exe.command_line_for_executing_program_via_command_line('exit(1)')),
                Arrangement(),
                Expectation(main_result=pfh_check.is_fail()),
        )


class TestValidation(TestCaseBaseForParser):
    def test_failing_validation_of_absolute_path(self):
        self._run(
                single_line_source('/absolute/path/to/program/that/does/not/exist'),
                Arrangement(),
                Expectation(validation_pre_eds=svh_check.is_validation_error()),
        )

    def test_failing_validation_of__rel_home_path(self):
        self._run(source_for_interpreting(options.REL_HOME_OPTION, 'non-existing-file.py'),
                  Arrangement(),
                  Expectation(validation_pre_eds=svh_check.is_validation_error()),
                  )

    def test_failing_validation_of__rel_tmp_path(self):
        self._run(source_for_interpreting(options.REL_TMP_OPTION, 'non-existing-file.py'),
                  Arrangement(),
                  Expectation(validation_post_eds=svh_check.is_validation_error()),
                  )

    def test_successful_validation(self):
        self._run(source_for_interpreting(options.REL_TMP_OPTION, 'existing-file.py'),
                  Arrangement(eds_contents_before_main=eds_populator.tmp_user_dir_contents(
                          DirContents([empty_file('existing-file.py')]))),
                  is_pass(),
                  )


_NO_OPTION = ''


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCasesThatTestIntegrationByAFewRandomTests))
    return ret_val


if __name__ == '__main__':
    unittest.main()
