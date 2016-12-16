import unittest

from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.file_structure_utils import tmp_dir_as_cwd
from exactly_lib_test.test_resources.value_assertions import value_assertion


class Arrangement:
    def __init__(self,
                 dir_contents_before: file_structure.DirContents = file_structure.DirContents([])):
        self.dir_contents_before = dir_contents_before


class Expectation:
    def __init__(self,
                 expected_action_result: value_assertion.ValueAssertion = value_assertion.anything_goes(),
                 expected_dir_contents_after: value_assertion.ValueAssertion = value_assertion.anything_goes()):
        self.expected_action_result = expected_action_result
        self.expected_dir_contents_after = expected_dir_contents_after


class TestCaseBase(unittest.TestCase):
    def _check(self,
               action_function,
               arrangement: Arrangement,
               expectation: Expectation):
        check(self,
              action_function,
              arrangement,
              expectation)


def check(put: unittest.TestCase,
          action_function,
          arrangement: Arrangement,
          expectation: Expectation):
    with tmp_dir_as_cwd(arrangement.dir_contents_before) as curr_dir_path:
        result = action_function()
        expectation.expected_action_result.apply(put, result)
        expectation.expected_dir_contents_after.apply(put, curr_dir_path)
