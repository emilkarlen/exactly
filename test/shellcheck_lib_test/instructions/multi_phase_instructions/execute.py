import sys
import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from shellcheck_lib.instructions.multi_phase_instructions import execute as sut
from shellcheck_lib.test_case.sections.common import HomeAndEds
from shellcheck_lib_test.instructions.test_resources.utils import single_line_source
from shellcheck_lib_test.util import home_and_eds_test
from shellcheck_lib_test.util import value_assertion as va


class ExecuteAction(home_and_eds_test.Action):
    def __init__(self,
                 setup: sut.Setup):
        self.setup = setup

    def apply(self, home_and_eds: HomeAndEds):
        return self.setup.execute(home_and_eds)


class TestCaseBase(home_and_eds_test.TestCaseBase):
    def _test_source(self,
                     source: SingleInstructionParserSource,
                     check: home_and_eds_test.Check):
        setup = sut.SetupParser().apply(source)
        action = ExecuteAction(setup)
        self._check_action(action,
                           check)


class ExitCodeIs(va.ValueAssertion):
    def __init__(self,
                 exit_code: int):
        self.exit_code = exit_code

    def apply(self, put: unittest.TestCase, value):
        put.assertEquals(self.exit_code,
                         value[0],
                         'Exit code')


class StderrContentsIs(va.ValueAssertion):
    def __init__(self,
                 stderr_contents: str):
        self.stderr_contents = stderr_contents

    def apply(self, put: unittest.TestCase, value):
        put.assertEqual(self.stderr_contents,
                        value[1],
                        'Stderr contents')


def result_is(exitcode: int,
              stderr_contents: str) -> va.ValueAssertion:
    return va.And([ExitCodeIs(exitcode),
                   StderrContentsIs(stderr_contents)])


class TestExecuteProgramWithShellArgumentList(TestCaseBase):
    def test_check_zero_exit_code(self):
        self._test_source(single_line_source(python_with_command_argument_on_command_line('exit(0)')),
                          home_and_eds_test.Check(expected_action_result=result_is(0,
                                                                                   None)))

    def test_check_non_zero_exit_code(self):
        self._test_source(single_line_source(python_with_command_argument_on_command_line('exit(1)')),
                          home_and_eds_test.Check(expected_action_result=result_is(1,
                                                                                   '')))

    def test_check_non_zero_exit_code_with_output_to_stderr(self):
        python_program = 'import sys; sys.stderr.write(\\"on stderr\\"); exit(2)'
        self._test_source(single_line_source(python_with_command_argument_on_command_line(python_program)),
                          home_and_eds_test.Check(expected_action_result=result_is(2,
                                                                                   'on stderr')))


def python_with_command_argument_on_command_line(command_argument: str) -> str:
    return '{} -c "{}"'.format(sys.executable, command_argument)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestExecuteProgramWithShellArgumentList))
    return ret_val


if __name__ == '__main__':
    unittest.main()
