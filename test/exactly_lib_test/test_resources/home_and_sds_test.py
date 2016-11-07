import unittest

from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib_test.test_resources.execution import sds_populator
from exactly_lib_test.test_resources.execution.utils import home_and_sds_and_test_as_curr_dir
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir_contents
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
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
                 sds_contents_before: sds_populator.SdsPopulator = sds_populator.empty(),
                 expected_action_result: ValueAssertion = anything_goes(),
                 expected_sds_contents_after: va.ValueAssertion = va.anything_goes(),
                 pre_action_action: Action = Action(),
                 post_action_check: PostActionCheck = PostActionCheck()):
        self.home_dir_contents_before = home_dir_contents_before
        self.sds_contents_before = sds_contents_before
        self.expected_action_result = expected_action_result
        self.expected_sds_contents_after = expected_sds_contents_after
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
                                           sds_contents=check.sds_contents_before) as home_and_sds:
        check.pre_action_action.apply(home_and_sds)
        result = action.apply(home_and_sds)
        check.expected_action_result.apply(put, result)
        check.expected_sds_contents_after.apply(put, home_and_sds.sds)
        check.post_action_check.apply(put, home_and_sds.sds)
