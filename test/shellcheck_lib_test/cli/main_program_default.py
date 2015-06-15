import io
import os
import unittest

from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib_test.util.with_tmp_file import tmp_file_containing, tmp_file_containing_lines
from shellcheck_lib.cli import main_program_default as sut


class TestTestCaseWithoutInstructions(unittest.TestCase):
    def test_empty_file(self):
        # ARRANGE #
        test_case_source = ''
        stdout_file = io.StringIO()
        with tmp_file_containing(test_case_source) as file_path:
            argv = [str(file_path)]
            # ACT #
            exit_status = sut.MainProgram(stdout_file).execute(argv)
            stdout_contents = stdout_file.getvalue()
            stdout_file.close()
        # ASSERT #
        self.assertEqual(0,
                         exit_status,
                         'Exit Status')
        self.assertEqual(FullResultStatus.PASS.name + os.linesep,
                         stdout_contents,
                         'Output on stdout')

    def test_empty_phases(self):
        # ARRANGE #
        test_case_lines = [
            '[setup]',
            '[act]',
            '[assert]',
            '[cleanup]',
        ]
        stdout_file = io.StringIO()
        with tmp_file_containing_lines(test_case_lines) as file_path:
            argv = [str(file_path)]
            # ACT #
            exit_status = sut.MainProgram(stdout_file).execute(argv)
            stdout_contents = stdout_file.getvalue()
            stdout_file.close()
        # ASSERT #
        self.assertEqual(0,
                         exit_status,
                         'Exit Status')
        self.assertEqual(FullResultStatus.PASS.name + os.linesep,
                         stdout_contents,
                         'Output on stdout')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestTestCaseWithoutInstructions))
    return ret_val


if __name__ == '__main__':
    unittest.main()
