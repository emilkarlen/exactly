import unittest

from shellcheck_lib.execution.result import FullResultStatus

from shellcheck_lib_test.util.expected_instruction_failure import ExpectedStatusAndFailure, \
    ExpectedInstructionFailureForNoFailure
from shellcheck_lib_test.util.with_tmp_file import tmp_file_containing, tmp_file_containing_lines
from shellcheck_lib.cli import parse_command_line_and_execute_test_case as sut


class TestTestCaseWithoutInstructions(unittest.TestCase):
    def test_empty_file(self):
        # ARRANGE #
        with tmp_file_containing('') as file_path:
            argv = [str(file_path)]
            # ACT #
            result = sut.execute(argv)
        # ASSERT #
        expected = ExpectedStatusAndFailure(
            FullResultStatus.PASS,
            ExpectedInstructionFailureForNoFailure())
        expected.assertions_on_status_and_failure(self,
                                                  result.full_result)

    def test_empty_phases(self):
        # ARRANGE #
        lines = [
            '[setup]',
            '[act]',
            '[assert]',
            '[cleanup]',
        ]
        with tmp_file_containing_lines(lines) as file_path:
            argv = [str(file_path)]
            # ACT #
            result = sut.execute(argv)
        # ASSERT #
        expected = ExpectedStatusAndFailure(
            FullResultStatus.PASS,
            ExpectedInstructionFailureForNoFailure())
        expected.assertions_on_status_and_failure(self,
                                                  result.full_result)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestTestCaseWithoutInstructions))
    return ret_val


if __name__ == '__main__':
    unittest.main()
