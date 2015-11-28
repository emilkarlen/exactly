import unittest

from shellcheck_lib.test_case.sections.common import HomeAndEds
from shellcheck_lib_test.instructions.test_resources import eds_populator, eds_contents_check
from shellcheck_lib_test.instructions.test_resources.utils import home_and_eds_and_test_as_curr_dir
from shellcheck_lib_test.util.file_structure import DirContents, empty_dir_contents
from . import tmp_dir_test


class PostActionCheck:
    def apply(self,
              put: unittest.TestCase,
              home_and_eds: HomeAndEds):
        pass


class Action:
    def apply(self, home_and_eds: HomeAndEds):
        return None


class Check:
    def __init__(self,
                 home_dir_contents_before: DirContents = empty_dir_contents(),
                 eds_contents_before: eds_populator.EdsPopulator = eds_populator.empty(),
                 expected_action_result: tmp_dir_test.ResultAssertion = tmp_dir_test.ResultAssertion(),
                 expected_eds_contents_after: eds_contents_check.Assertion = eds_contents_check.AnythingGoes(),
                 pre_action_action: Action = Action(),
                 post_action_check: PostActionCheck = PostActionCheck()):
        self.home_dir_contents_before = home_dir_contents_before
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
    with home_and_eds_and_test_as_curr_dir(home_dir_contents=check.home_dir_contents_before,
                                           eds_contents=check.eds_contents_before) as home_and_eds:
        check.pre_action_action.apply(home_and_eds)
        result = action.apply(home_and_eds)
        check.expected_action_result.apply(put, result)
        check.expected_eds_contents_after.apply(put, home_and_eds.eds)
        check.post_action_check.apply(put, home_and_eds.eds)
