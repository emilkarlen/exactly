import pathlib
import unittest
import sys

from shellcheck_lib.execution.result import FullResultStatus

from shellcheck_lib_test.util.with_tmp_file import lines_content, run_subprocess_with_file_arg, SubProcessResult, \
    ExpectedSubProcessResult


SRC_DIR_NAME = 'src'
MAIN_PROGRAM_FILE_NAME = 'shellcheck.py'


def shellcheck_src_path(dir_of_this_file: pathlib.Path) -> pathlib.Path:
    return dir_of_this_file.parent / SRC_DIR_NAME / MAIN_PROGRAM_FILE_NAME


class TestCase(unittest.TestCase):
    def test_empty_test_case__invoked_with_no_cli_flags(self):
        # ARRANGE #
        test_case_source = ''
        # ACT #
        actual = self._run_shellcheck_in_sub_process(test_case_source)
        # ASSERT #
        SUCCESSFUL_RESULT.assert_matches(self,
                                         actual)

    def test_test_case_with_only_phase_headers(self):
        # ARRANGE #
        test_case_source_lines = [
            '[setup]',
            '[act]',
            '[assert]',
            '[cleanup]',
        ]
        test_case_source = lines_content(test_case_source_lines)
        # ACT #
        actual = self._run_shellcheck_in_sub_process(test_case_source)
        # ASSERT #
        SUCCESSFUL_RESULT.assert_matches(self,
                                         actual)

    def _run_shellcheck_in_sub_process(self,
                                       test_case_source: str,
                                       flags: list=()) -> SubProcessResult:
        return run_shellcheck_in_sub_process(self,
                                             test_case_source=test_case_source,
                                             flags=flags)


SUCCESSFUL_RESULT = ExpectedSubProcessResult(exitcode=FullResultStatus.PASS.value,
                                             stdout=lines_content([FullResultStatus.PASS.name]),
                                             stderr='')


def run_shellcheck_in_sub_process(puc: unittest.TestCase,
                                  test_case_source: str,
                                  flags: list=()) -> SubProcessResult:
    cwd = pathlib.Path.cwd()
    # print('# DEBUG: cwd: ' + str(cwd))
    if not sys.executable:
        puc.fail('Cannot execute test since the name of the Python 3 interpreter is not found in sys.executable.')
    shellcheck_path = shellcheck_src_path(cwd)
    args_without_file = [sys.executable, str(shellcheck_path)] + list(flags)
    return run_subprocess_with_file_arg(args_without_file, test_case_source)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCase))
    return ret_val


if __name__ == '__main__':
    unittest.main()
