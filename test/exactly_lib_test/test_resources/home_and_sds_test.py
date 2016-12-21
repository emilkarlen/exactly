import unittest

from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib_test.test_resources.execution import sds_populator
from exactly_lib_test.test_resources.execution.utils import home_and_sds_with_act_as_curr_dir
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


class Arrangement:
    def __init__(self,
                 home_dir_contents_before: DirContents = empty_dir_contents(),
                 sds_contents_before: sds_populator.SdsPopulator = sds_populator.empty(),
                 pre_action_action: Action = Action()):
        self.home_dir_contents_before = home_dir_contents_before
        self.sds_contents_before = sds_contents_before
        self.pre_action_action = pre_action_action


class Expectation:
    def __init__(self,
                 expected_action_result: ValueAssertion = anything_goes(),
                 expected_sds_contents_after: va.ValueAssertion = va.anything_goes(),
                 post_action_check: PostActionCheck = PostActionCheck()):
        self.expected_action_result = expected_action_result
        self.expected_sds_contents_after = expected_sds_contents_after
        self.post_action_check = post_action_check


class TestCaseBase(unittest.TestCase):
    def _check(self,
               action: Action,
               arrangement: Arrangement,
               expectation: Expectation):
        check(self,
              action,
              arrangement,
              expectation)


def check(put: unittest.TestCase,
          action: Action,
          arrangement: Arrangement,
          expectation: Expectation):
    with home_and_sds_with_act_as_curr_dir(home_dir_contents=arrangement.home_dir_contents_before,
                                           sds_contents=arrangement.sds_contents_before) as home_and_sds:
        arrangement.pre_action_action.apply(home_and_sds)
        result = action.apply(home_and_sds)
        expectation.expected_action_result.apply(put, result)
        expectation.expected_sds_contents_after.apply(put, home_and_sds.sds)
        expectation.post_action_check.apply(put, home_and_sds.sds)
