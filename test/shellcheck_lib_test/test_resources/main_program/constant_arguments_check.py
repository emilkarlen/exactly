"""
Structures for tests that only uses constant command line arguments.
Especially, no temporary files need to be generated.
"""
import unittest

from shellcheck_lib_test.test_resources import value_assertion
from shellcheck_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


class Arrangement:
    def command_line_arguments(self) -> list:
        raise NotImplementedError()


class PlainArrangement(Arrangement):
    def __init__(self,
                 command_line_arguments: list):
        self._command_line_arguments = command_line_arguments

    def command_line_arguments(self) -> list:
        return self._command_line_arguments


class ProcessTestCase:
    """
    A test case with name, arrangement and expectation.
    """

    def __init__(self,
                 name: str,
                 arrangement: Arrangement,
                 assertion: value_assertion.ValueAssertion):
        self._name = name
        self._arrangement = arrangement
        self._assertion = assertion

    @property
    def name(self) -> str:
        return self._name

    @property
    def arrangement(self) -> Arrangement:
        return self._arrangement

    @property
    def assertion(self) -> value_assertion.ValueAssertion:
        """
        :rtype: An assertion on a SubProcessResult.
        """
        return self._assertion


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
        message_builder = value_assertion.MessageBuilder('(stderr = "%s")' % sub_process_result.stderr)
        self.test_case.assertion.apply(self, sub_process_result, message_builder)

    def shortDescription(self):
        return self.test_case.name + '/' + self.main_program_runner.description_for_test_name()
