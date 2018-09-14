import unittest

from exactly_lib_test.processing.standalone.test_resources.instructions_inclusion_test_base import \
    TestInclusionOfCaseContentsFromSuiteTestBase
from exactly_lib_test.processing.standalone.test_resources.run_test_case import TestCaseRunner


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(TestInclusionOfCaseContentsFromSuiteTestBase):
    runner = TestCaseRunner()

    def test_setup_instructions_in_containing_suite_SHOULD_be_executed_first_in_the_case(self):
        self._setup_instructions_in_containing_suite_SHOULD_be_executed_first_in_the_case(self.runner)
