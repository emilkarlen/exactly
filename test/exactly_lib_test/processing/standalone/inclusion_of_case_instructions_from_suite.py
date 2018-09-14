import unittest

from exactly_lib_test.processing.standalone.test_resources.instructions_inclusion_test_base import \
    ContentsFromSuiteShouldBeIncludedInTheCaseTestBase
from exactly_lib_test.processing.standalone.test_resources.run_test_case import TestCaseRunner


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(SetupSectionContentsFromSuiteShouldBeIncludedInTheCaseTest)


class SetupSectionContentsFromSuiteShouldBeIncludedInTheCaseTest(ContentsFromSuiteShouldBeIncludedInTheCaseTestBase):
    runner = TestCaseRunner()

    def test_setup_instructions_in_suite__explicit_suite_argument(self):
        self._setup_instructions_in_suite__explicit_suite_argument(self.runner)

    def test_setup_instructions_in_suite__implicit_default_suite(self):
        self._setup_instructions_in_suite__implicit_default_suite(self.runner)
