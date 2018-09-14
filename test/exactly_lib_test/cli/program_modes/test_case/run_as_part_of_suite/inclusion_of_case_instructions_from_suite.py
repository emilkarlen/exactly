import unittest
from pathlib import Path

from exactly_lib.cli.main_program import TestSuiteDefinition
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib_test.cli.program_modes.test_case.run_as_part_of_suite.test_resources.run_test_case import run_test_case
from exactly_lib_test.processing.standalone.test_resources.instructions_inclusion_test_base import \
    TestInclusionOfCaseContentsFromSuiteTestBase, TestCaseRunner
from exactly_lib_test.test_resources.process import SubProcessResult


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class _TestCaseRunner(TestCaseRunner):
    def run(self,
            parsing_setup: TestCaseParsingSetup,
            test_case_handling_setup: TestCaseHandlingSetup,
            test_suite_definition: TestSuiteDefinition,
            case_file: Path,
            suite_file: Path) -> SubProcessResult:
        return run_test_case(parsing_setup,
                             test_case_handling_setup,
                             test_suite_definition,
                             case_file,
                             suite_file)


class Test(TestInclusionOfCaseContentsFromSuiteTestBase):
    _runner = _TestCaseRunner()

    def test_setup_instructions_in_containing_suite_SHOULD_be_executed_first_in_the_case(self):
        self._setup_instructions_in_containing_suite_SHOULD_be_executed_first_in_the_case(self._runner)
