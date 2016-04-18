import unittest

from shellcheck_lib_test.test_resources.main_program.constant_arguments_check import ProcessTestCase
from shellcheck_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


class TestCaseForProcessTestCase(unittest.TestCase):
    def __init__(self,
                 test_case: ProcessTestCase,
                 main_program_runner: MainProgramRunner):
        super().__init__()
        self.test_case = test_case
        self.main_program_runner = main_program_runner

    def runTest(self):
        command_line_arguments = self.test_case.arrangement.command_line_arguments()
        sub_process_result = self.main_program_runner.run(self, command_line_arguments)
        self.test_case.assertion.apply(self, sub_process_result)

    def shortDescription(self):
        return self.test_case.name + '/' + self.main_program_runner.description_for_test_name()


def test_suite_for_test_cases(test_cases: list, main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    """
    :type test_cases: [ProcessTestCase]
    """
    return unittest.TestSuite([
                                  TestCaseForProcessTestCase(tc, main_program_runner)
                                  for tc in test_cases
                                  ])
