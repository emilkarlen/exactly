import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from shellcheck_lib.instructions.multi_phase_instructions import execute as sut
from shellcheck_lib.instructions.utils.sub_process_execution import InstructionMetaInfo
from shellcheck_lib.test_case.sections.common import HomeAndEds
from shellcheck_lib_test.instructions.test_resources.utils import single_line_source
from shellcheck_lib_test.test_resources import python_program_execution as py_exe
from shellcheck_lib_test.util import home_and_eds_test
from shellcheck_lib_test.util import value_assertion as va


class ExecuteAction(home_and_eds_test.Action):
    def __init__(self,
                 setup: sut.Setup):
        self.setup = setup

    def apply(self, home_and_eds: HomeAndEds) -> sut.ResultAndStderr:
        return sut.execute_setup_and_read_stderr_if_non_zero_exitcode(self.setup, home_and_eds)


class TestCaseBase(home_and_eds_test.TestCaseBase):
    def _test_source(self,
                     source: SingleInstructionParserSource,
                     check: home_and_eds_test.Check):
        instruction_meta_info = InstructionMetaInfo('phase-name',
                                                    'instruction-name')
        setup = sut.SetupParser(instruction_meta_info).apply(source)
        action = ExecuteAction(setup)
        self._check_action(action,
                           check)


class IsSuccess(va.ValueAssertion):
    def apply(self, put: unittest.TestCase, value: sut.ResultAndStderr):
        put.assertTrue(value.result.is_success,
                       'Result is expected to indicate success')


class IsFailure(va.ValueAssertion):
    def apply(self, put: unittest.TestCase, value: sut.ResultAndStderr):
        put.assertFalse(value.result.is_success,
                        'Result is expected to indicate failure')


class ExitCodeIs(va.ValueAssertion):
    def __init__(self,
                 exit_code: int):
        self.exit_code = exit_code

    def apply(self, put: unittest.TestCase, value: sut.ResultAndStderr):
        put.assertEquals(self.exit_code,
                         value.result.exit_code,
                         'Exit code')


class StderrContentsIs(va.ValueAssertion):
    def __init__(self,
                 stderr_contents: str):
        self.stderr_contents = stderr_contents

    def apply(self, put: unittest.TestCase, value: sut.ResultAndStderr):
        put.assertEqual(self.stderr_contents,
                        value.stderr_contents,
                        'Stderr contents')


def is_success_result(exitcode: int,
                      stderr_contents: str) -> va.ValueAssertion:
    return va.And([IsSuccess(),
                   ExitCodeIs(exitcode),
                   StderrContentsIs(stderr_contents)])


class TestExecuteProgramWithShellArgumentList(TestCaseBase):
    def test_check_zero_exit_code(self):
        self._test_source(single_line_source(py_exe.command_line_for_executing_program_via_command_line('exit(0)')),
                          home_and_eds_test.Check(expected_action_result=is_success_result(0,
                                                                                           None)))

    def test_check_non_zero_exit_code(self):
        self._test_source(single_line_source(py_exe.command_line_for_executing_program_via_command_line('exit(1)')),
                          home_and_eds_test.Check(expected_action_result=is_success_result(1,
                                                                                           '')))

    def test_check_non_zero_exit_code_with_output_to_stderr(self):
        python_program = 'import sys; sys.stderr.write(\\"on stderr\\"); exit(2)'
        self._test_source(
            single_line_source(py_exe.command_line_for_executing_program_via_command_line(python_program)),
            home_and_eds_test.Check(expected_action_result=is_success_result(2,
                                                                             'on stderr')))

    def test_invalid_executable(self):
        self._test_source(single_line_source('/not/an/executable/program'),
                          home_and_eds_test.Check(expected_action_result=IsFailure()))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestExecuteProgramWithShellArgumentList))
    return ret_val


if __name__ == '__main__':
    unittest.main()
