import unittest

from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib_test.test_resources.execution import sds_populator, eds_contents_check
from exactly_lib_test.test_resources.execution.utils import home_and_sds_and_test_as_curr_dir
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir_contents
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, anything_goes


class PostActionCheck:
    def apply(self,
              put: unittest.TestCase,
              home_and_sds: HomeAndSds):
        pass


class Action:
    def apply(self, home_and_sds: HomeAndSds):
        return None


class Check:
    def __init__(self,
                 home_dir_contents_before: DirContents = empty_dir_contents(),
                 eds_contents_before: sds_populator.EdsPopulator = sds_populator.empty(),
                 expected_action_result: ValueAssertion = anything_goes(),
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
    with home_and_sds_and_test_as_curr_dir(home_dir_contents=check.home_dir_contents_before,
                                           eds_contents=check.eds_contents_before) as home_and_sds:
        check.pre_action_action.apply(home_and_sds)
        result = action.apply(home_and_sds)
        check.expected_action_result.apply(put, result)
        check.expected_eds_contents_after.apply(put, home_and_sds.sds)
        check.post_action_check.apply(put, home_and_sds.sds)
