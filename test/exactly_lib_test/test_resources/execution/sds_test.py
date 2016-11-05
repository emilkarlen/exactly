import os
import unittest

from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_resources.execution import sds_populator, sds_contents_check
from exactly_lib_test.test_resources.execution.utils import sandbox_directory_structure
from exactly_lib_test.test_resources.file_checks import FileChecker
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, anything_goes


class PostActionCheck:
    def apply(self,
              put: unittest.TestCase,
              sds: SandboxDirectoryStructure):
        pass


class Action:
    def apply(self, sds: SandboxDirectoryStructure):
        return None


class Check:
    def __init__(self,
                 eds_contents_before: sds_populator.EdsPopulator = sds_populator.empty(),
                 expected_action_result: ValueAssertion = anything_goes(),
                 expected_eds_contents_after: sds_contents_check.Assertion = sds_contents_check.AnythingGoes(),
                 pre_action_action: Action = Action(),
                 post_action_check: PostActionCheck = PostActionCheck()):
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
    with sandbox_directory_structure(check.eds_contents_before) as sds:
        os.chdir(str(sds.act_dir))
        try:
            check.pre_action_action.apply(sds)
            result = action.apply(sds)
            check.expected_action_result.apply(put, result)
            check.expected_eds_contents_after.apply(put, sds)
            check.post_action_check.apply(put, sds)
        finally:
            os.chdir(original_cwd)


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
