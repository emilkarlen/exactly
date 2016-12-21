import unittest

from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_resources.assertions.file_checks import FileChecker
from exactly_lib_test.test_resources.execution.sds_check import sds_populator
from exactly_lib_test.test_resources.execution.sds_check.sds_utils import SdsAction, sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


class PostActionCheck:
    def apply(self,
              put: unittest.TestCase,
              sds: SandboxDirectoryStructure):
        pass


class Arrangement:
    def __init__(self,
                 sds_contents_before: sds_populator.SdsPopulator = sds_populator.empty(),
                 pre_contents_population_action: SdsAction = SdsAction(),
                 pre_action_action: SdsAction = SdsAction()):
        self.pre_contents_population_action = pre_contents_population_action
        self.sds_contents_before = sds_contents_before
        self.pre_action_action = pre_action_action


class Expectation:
    def __init__(self,
                 expected_action_result: va.ValueAssertion = va.anything_goes(),
                 expected_sds_contents_after: va.ValueAssertion = va.anything_goes(),
                 post_action_check: PostActionCheck = PostActionCheck()):
        self.expected_action_result = expected_action_result
        self.expected_sds_contents_after = expected_sds_contents_after
        self.post_action_check = post_action_check


class TestCaseBase(unittest.TestCase):
    def _check(self,
               action: SdsAction,
               arrangement: Arrangement,
               expectation: Expectation):
        check(self,
              action,
              arrangement,
              expectation)


def check(put: unittest.TestCase,
          action: SdsAction,
          arrangement: Arrangement,
          expectation: Expectation):
    with sds_with_act_as_curr_dir(contents=arrangement.sds_contents_before,
                                  pre_contents_population_action=arrangement.pre_contents_population_action) as sds:
        arrangement.pre_action_action.apply(sds)
        result = action.apply(sds)
        expectation.expected_action_result.apply(put, result)
        expectation.expected_sds_contents_after.apply(put, sds)
        expectation.post_action_check.apply(put, sds)


class ResultFilesCheck(PostActionCheck):
    def __init__(self,
                 expected_exitcode: int,
                 expected_stdout_contents: str,
                 expected_stderr_contents: str):
        self.expected_exitcode = expected_exitcode
        self.expected_stdout_contents = expected_stdout_contents
        self.expected_stderr_contents = expected_stderr_contents

    def apply(self, put: unittest.TestCase, sds: SandboxDirectoryStructure):
        fc = FileChecker(put, 'Result files: ')
        fc.assert_is_plain_file_with_contents(sds.result.exitcode_file,
                                              str(self.expected_exitcode))
        fc.assert_is_plain_file_with_contents(sds.result.stdout_file,
                                              self.expected_stdout_contents)
        fc.assert_is_plain_file_with_contents(sds.result.stderr_file,
                                              self.expected_stderr_contents)
