import os
import unittest

from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib_test.instructions.test_resources import eds_populator, eds_contents_check
from shellcheck_lib_test.instructions.test_resources.utils import execution_directory_structure
from . import tmp_dir_test


class PostActionCheck:
    def apply(self,
              put: unittest.TestCase,
              eds: ExecutionDirectoryStructure):
        pass


class Action:
    def apply(self, eds: ExecutionDirectoryStructure):
        return None


class Check:
    def __init__(self,
                 eds_contents_before: eds_populator.EdsPopulator=eds_populator.empty(),
                 expected_action_result: tmp_dir_test.ResultAssertion=tmp_dir_test.ResultAssertion(),
                 expected_eds_contents_after: eds_contents_check.Assertion=eds_contents_check.AnythingGoes(),
                 pre_action_action: Action=Action(),
                 post_action_check: PostActionCheck=PostActionCheck()):
        self.eds_contents_before = eds_contents_before
        self.expected_action_result = expected_action_result
        self.expected_eds_contents_after = expected_eds_contents_after
        self.pre_action_action = pre_action_action
        self.post_action_check = post_action_check


class TestCaseBase(unittest.TestCase):
    def _check_action(self,
                      action: Action,
                      check: Check):
        execute(self,
                action,
                check)


def execute(put: unittest.TestCase,
            action: Action,
            check: Check):
    original_cwd = os.getcwd()
    with execution_directory_structure(check.eds_contents_before) as eds:
        os.chdir(str(eds.act_dir))
        try:
            check.pre_action_action.apply(eds)
            result = action.apply(eds)
            check.expected_action_result.apply(put, result)
            check.expected_eds_contents_after.apply(put, eds)
            check.post_action_check.apply(put, eds)
        finally:
            os.chdir(original_cwd)
