import unittest

from exactly_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from exactly_lib_test.test_resources import file_structure, file_checks
from exactly_lib_test.test_resources.value_assertion import ValueAssertion


class Assertion:
    def apply(self,
              put: unittest.TestCase,
              eds: ExecutionDirectoryStructure):
        raise NotImplementedError()


class AnythingGoes(Assertion):
    def apply(self,
              put: unittest.TestCase,
              eds: ExecutionDirectoryStructure):
        pass


class UnconditionalFail(Assertion):
    def apply(self,
              put: unittest.TestCase,
              eds: ExecutionDirectoryStructure):
        put.fail('Unconditional fail')


class ActRootContainsExactly(Assertion):
    def __init__(self,
                 expected_contents: file_structure.DirContents):
        self.expected_contents = expected_contents

    def apply(self,
              put: unittest.TestCase,
              eds: ExecutionDirectoryStructure):
        checker = file_checks.FileChecker(put,
                                          message_header='Contents of act directory')
        checker.assert_dir_contents_matches_exactly(eds.act_dir,
                                                    self.expected_contents)


class TestCaseRootContainsExactly(Assertion):
    def __init__(self,
                 expected_contents: file_structure.DirContents):
        self.expected_contents = expected_contents

    def apply(self,
              put: unittest.TestCase,
              eds: ExecutionDirectoryStructure):
        checker = file_checks.FileChecker(put,
                                          message_header='Contents of testcase directory')
        checker.assert_dir_contents_matches_exactly(eds.test_case_dir,
                                                    self.expected_contents)


class TmpUserRootContainsExactly(Assertion):
    def __init__(self,
                 expected_contents: file_structure.DirContents):
        self.expected_contents = expected_contents

    def apply(self,
              put: unittest.TestCase,
              eds: ExecutionDirectoryStructure):
        checker = file_checks.FileChecker(put,
                                          message_header='Contents of tmp/user directory')
        checker.assert_dir_contents_matches_exactly(eds.tmp.user_dir,
                                                    self.expected_contents)


class AdaptVa(Assertion):
    def __init__(self,
                 va: ValueAssertion):
        self.va = va

    def apply(self,
              put: unittest.TestCase,
              eds: ExecutionDirectoryStructure):
        self.va.apply(put, eds)
