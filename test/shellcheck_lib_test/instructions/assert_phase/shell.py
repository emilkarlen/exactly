import unittest
import sys

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib_test.instructions.test_resources import pfh_check
from shellcheck_lib_test.instructions.assert_phase.test_resources.instruction_check import Flow, TestCaseBase
from shellcheck_lib.instructions.assert_phase import shell as sut
from shellcheck_lib_test.instructions.test_resources.utils import new_source
from shellcheck_lib_test.util.file_utils import tmp_file_containing


class TestParse(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        source = new_source('instruction-name', '   ')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)


class TestExecution(TestCaseBase):
    def test_instruction_is_successful_when_exit_status_from_command_is_0(self):
        script_that_exists_with_status_0 = """
import sys
sys.exit(0)
"""
        with tmp_file_containing(script_that_exists_with_status_0,
                                 suffix='.py') as script_file_path:
            self._check(
                Flow(sut.Parser()),
                new_source('instruction-name',
                           '{} {}'.format(sys.executable,
                                          str(script_file_path))))

    def test_instruction_is_hard_error_WHEN_exit_status_from_command_is_not_0(self):
        script_that_exists_with_status_0 = """
import sys
sys.exit(1)
"""
        with tmp_file_containing(script_that_exists_with_status_0,
                                 suffix='.py') as script_file_path:
            self._check(
                Flow(sut.Parser(),
                     expected_main_result=pfh_check.is_fail()),
                new_source('instruction-name',
                           '{} {}'.format(sys.executable,
                                          str(script_file_path))))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    ret_val.addTest(unittest.makeSuite(TestExecution))
    return ret_val


if __name__ == '__main__':
    unittest.main()
