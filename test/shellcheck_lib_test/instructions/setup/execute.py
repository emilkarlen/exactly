import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from shellcheck_lib.instructions.multi_phase_instructions.execute import INTERPRET_OPTION
from shellcheck_lib.instructions.setup import execute as sut
from shellcheck_lib.instructions.utils.relative_path_options import REL_HOME_OPTION, REL_TMP_OPTION
from shellcheck_lib_test.instructions.multi_phase_instructions.execute import \
    py_pgm_that_exits_with_value_on_command_line
from shellcheck_lib_test.instructions.setup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation, is_success
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources.utils import single_line_source
from shellcheck_lib_test.test_resources import python_program_execution as py_exe
from shellcheck_lib_test.util.file_structure import DirContents
from shellcheck_lib_test.util.file_structure import File


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             source: SingleInstructionParserSource,
             arrangement: Arrangement,
             expectation: Expectation):
        self._check(sut.parser('instruction-name'), source, arrangement, expectation)


class TestExecuteIntegrationByAFewRandomTests(TestCaseBaseForParser):
    def test_successful_execution(self):
        self._run(single_line_source(py_exe.command_line_for_executing_program_via_command_line('exit(0)')),
                  Arrangement(),
                  is_success())

    def test_failing_execution(self):
        self._run(single_line_source(py_exe.command_line_for_executing_program_via_command_line('exit(1)')),
                  Arrangement(),
                  Expectation(main_result=sh_check.IsHardError()))

    def test_failing_validation(self):
        self._run(single_line_source('/absolute/path/to/program/that/does/not/exist'),
                  Arrangement(),
                  Expectation(pre_validation_result=svh_check.is_validation_error()))


class TestInterpretIntegrationByAFewRandomTests(TestCaseBaseForParser):
    def test_check_zero_exit_code__rel_home_default(self):
        self._run(single_line_source(py_exe.command_line_for_arguments([INTERPRET_OPTION,
                                                                        'exit-with-value-on-command-line.py',
                                                                        0])),
                  _arrangement_for_pgm_that_exits_with_cla__rel_home('exit-with-value-on-command-line.py'),
                  Expectation())

    def test_check_non_zero_exit_code__rel_home(self):
        self._run(single_line_source(py_exe.command_line_for_arguments([INTERPRET_OPTION,
                                                                        REL_HOME_OPTION,
                                                                        'exit-with-value-on-command-line.py',
                                                                        3])),
                  _arrangement_for_pgm_that_exits_with_cla__rel_home('exit-with-value-on-command-line.py'),
                  Expectation(main_result=sh_check.IsHardError()))

    def test_non_existing_source_file_argument__pre_eds(self):
        self._run(single_line_source(py_exe.command_line_for_arguments([INTERPRET_OPTION,
                                                                        'non-existing-file-rel-home.py',
                                                                        ])),
                  Arrangement(),
                  Expectation(pre_validation_result=svh_check.is_validation_error()))

    def test_non_existing_source_file_argument__post_eds(self):
        self._run(single_line_source(py_exe.command_line_for_arguments([INTERPRET_OPTION,
                                                                        REL_TMP_OPTION,
                                                                        'non-existing-file-rel-tmp.py',
                                                                        ])),
                  Arrangement(),
                  Expectation(main_result=sh_check.IsHardError()))


def _arrangement_for_pgm_that_exits_with_cla__rel_home(source_file_name: str):
    return Arrangement(home_dir_contents=DirContents([
        File(source_file_name,
             py_pgm_that_exits_with_value_on_command_line(''))])
    )


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestExecuteIntegrationByAFewRandomTests))
    ret_val.addTest(unittest.makeSuite(TestInterpretIntegrationByAFewRandomTests))
    return ret_val


if __name__ == '__main__':
    unittest.main()
