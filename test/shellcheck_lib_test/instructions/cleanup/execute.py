import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from shellcheck_lib.instructions.cleanup import execute as sut
from shellcheck_lib_test.instructions.cleanup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources.utils import single_line_source
from shellcheck_lib_test.test_resources import python_program_execution as py_exe


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
                  Expectation(),
                  )

    def test_failing_execution(self):
        self._run(single_line_source(py_exe.command_line_for_executing_program_via_command_line('exit(1)')),
                  Arrangement(),
                  Expectation(main_result=sh_check.IsHardError()),
                  )

    def test_failing_validation(self):
        self._run(single_line_source('/absolute/path/to/program/that/does/not/exist'),
                  Arrangement(),
                  Expectation(main_result=sh_check.IsHardError()),
                  )


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCasesThatTestIntegrationByAFewRandomTests))
    return ret_val


if __name__ == '__main__':
    unittest.main()
