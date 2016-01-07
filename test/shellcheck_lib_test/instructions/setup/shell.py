import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from shellcheck_lib.instructions.setup import shell as sut
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib_test.instructions.setup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation, is_success
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources.check_description import TestDescriptionBase
from shellcheck_lib_test.instructions.test_resources.utils import new_source2
from shellcheck_lib_test.test_resources import python_program_execution as py_exe
from shellcheck_lib_test.test_resources.file_utils import tmp_file_containing


class TestParse(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        source = new_source2('   ')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parser().apply(source)


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             source: SingleInstructionParserSource,
             arrangement: Arrangement,
             expectation: Expectation):
        self._check(sut.parser(), source, arrangement, expectation)


class TestExecution(TestCaseBaseForParser):
    def test_instruction_is_successful_when_exit_status_from_command_is_0(self):
        script_that_exists_with_status_0 = """
import sys
sys.exit(0)
"""
        with tmp_file_containing(script_that_exists_with_status_0,
                                 suffix='.py') as script_file_path:
            self._run(new_source2(py_exe.command_line_for_interpreting(script_file_path)),
                      Arrangement(),
                      is_success()
                      )

    def test_instruction_is_hard_error_WHEN_exit_status_from_command_is_not_0(self):
        script_that_exists_with_status_0 = """
import sys
sys.exit(1)
"""
        with tmp_file_containing(script_that_exists_with_status_0,
                                 suffix='.py') as script_file_path:
            self._run(new_source2(py_exe.command_line_for_interpreting(script_file_path)),
                      Arrangement(),
                      Expectation(main_result=sh_check.IsHardError())
                      )


class TestDescription(TestDescriptionBase):
    def _description(self) -> Description:
        return sut.description('instruction name')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    ret_val.addTest(unittest.makeSuite(TestExecution))
    ret_val.addTest(unittest.makeSuite(TestDescription))
    return ret_val


if __name__ == '__main__':
    unittest.main()
