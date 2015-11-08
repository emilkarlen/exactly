import unittest

from shellcheck_lib_test.util import file_structure
from shellcheck_lib_test.util import file_checks
from shellcheck_lib_test.util.file_structure_utils import tmp_dir_as_cwd


class ResultAssertion:
    def apply(self,
              put: unittest.TestCase,
              result):
        pass


class Check:
    def __init__(self,
                 dir_contents_before: file_structure.DirContents=file_structure.DirContents([]),
                 expected_action_result: ResultAssertion=ResultAssertion(),
                 expected_dir_contents_after: file_checks.Assertion=file_checks.AnythingGoes()):
        self.dir_contents_before = dir_contents_before
        self.expected_action_result = expected_action_result
        self.expected_dir_contents_after = expected_dir_contents_after


class TestCaseBase(unittest.TestCase):
    def _check_action(self,
                      action_function,
                      check: Check):
        execute(self,
                action_function,
                check)


class ResultIsNone(ResultAssertion):
    def apply(self,
              put: unittest.TestCase,
              result):
        put.assertIsNone(result)


class ResultIsNotNone(ResultAssertion):
    def apply(self,
              put: unittest.TestCase,
              result):
        put.assertIsNotNone(result)


def execute(put: unittest.TestCase,
            action_function,
            check: Check):
    with tmp_dir_as_cwd(check.dir_contents_before) as curr_dir_path:
        result = action_function()
        check.expected_action_result.apply(put, result)
        check.expected_dir_contents_after.apply(put, curr_dir_path)
