import unittest

from shellcheck_lib.instructions.cleanup import execute as sut
from shellcheck_lib_test.instructions.cleanup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources.utils import single_line_source
from shellcheck_lib_test.test_resources import python_program_execution as py_exe


class TestCasesThatTestIntegrationByAFewRandomTests(TestCaseBase):
    def test_successful_execution(self):
        self._check(_PARSER,
                    Arrangement(),
                    Expectation(),
                    single_line_source(py_exe.command_line_for_executing_program_via_command_line('exit(0)')))

    def test_failing_execution(self):
        self._check(_PARSER,
                    Arrangement(),
                    Expectation(main_result=sh_check.IsHardError()),
                    single_line_source(py_exe.command_line_for_executing_program_via_command_line('exit(1)')))

    def test_failing_validation(self):
        self._check(_PARSER,
                    Arrangement(),
                    Expectation(main_result=sh_check.IsHardError()),
                    single_line_source('/absolute/path/to/program/that/does/not/exist'))


_PARSER = sut.parser('instruction-name')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCasesThatTestIntegrationByAFewRandomTests))
    return ret_val


if __name__ == '__main__':
    unittest.main()
