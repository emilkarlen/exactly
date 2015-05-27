import os
import pathlib
import unittest
import sys

from shelltest.execution.result import FullResultStatus
from shelltest_test.util.with_tmp_file import lines_content, run_subprocess_with_file_arg


SRC_DIR_NAME = 'src'
MAIN_PROGRAM_FILE_NAME = 'shellcheck.py'


def shellcheck_src_path(dir_of_this_file: pathlib.Path) -> pathlib.Path:
    return dir_of_this_file.parent / SRC_DIR_NAME / MAIN_PROGRAM_FILE_NAME


class TestCase(unittest.TestCase):
    def test_successful_test_case(self):
        # ARRANGE #
        lines = [
            '[setup]',
            '# TODO: add instruction',
            '[act]',
            '# TODO: add instruction',
            '[assert]',
            '# TODO: add instruction',
            '[cleanup]',
            '# TODO: add instruction',
        ]

        cwd = pathlib.Path.cwd()
        # print('# DEBUG: cwd: ' + str(cwd))
        if not sys.executable:
            self.fail('Cannot execute test since name of executable not found in sys.executable.')
        shellcheck_path = shellcheck_src_path(cwd)
        args_without_file = [sys.executable, str(shellcheck_path)]
        # ACT #
        result = run_subprocess_with_file_arg(args_without_file, lines_content(lines))
        # ASSERT #
        self.assertEqual(FullResultStatus.PASS.value,
                         result.exitcode,
                         'Exit code')
        self.assertEqual(FullResultStatus.PASS.name + os.linesep,
                         result.stdout,
                         'Content on stdout')
        self.assertEqual('',
                         result.stderr,
                         'Content on stderr')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCase))
    return ret_val


if __name__ == '__main__':
    unittest.main()
