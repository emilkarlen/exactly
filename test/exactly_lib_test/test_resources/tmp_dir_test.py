import unittest

from exactly_lib_test.test_resources import file_checks
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.file_structure_utils import tmp_dir_as_cwd
from . import value_assertion


class Check:
    def __init__(self,
                 dir_contents_before: file_structure.DirContents = file_structure.DirContents([]),
                 expected_action_result: value_assertion.ValueAssertion = value_assertion.anything_goes(),
                 expected_dir_contents_after: file_checks.Assertion = file_checks.AnythingGoes()):
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


def execute(put: unittest.TestCase,
            action_function,
            check: Check):
    with tmp_dir_as_cwd(check.dir_contents_before) as curr_dir_path:
        result = action_function()
        check.expected_action_result.apply(put, result)
        check.expected_dir_contents_after.apply(put, curr_dir_path)
