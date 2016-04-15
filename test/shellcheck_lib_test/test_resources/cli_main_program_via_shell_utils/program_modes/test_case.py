import unittest

from shellcheck_lib.cli.main_program import EXIT_INVALID_USAGE
from shellcheck_lib_test.cli.test_resources.execute_main_program import arguments_for_test_interpreter_and_more_tuple
from shellcheck_lib_test.test_resources.file_utils import tmp_file_containing
from shellcheck_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from shellcheck_lib_test.test_resources.process import SubProcessResultInfo


class TestCaseFileArgumentArrangement:
    def __init__(self,
                 test_case_contents: str = '',
                 arguments_before_file_argument: iter = ()):
        self.test_case_contents = test_case_contents
        self._arguments_before_file_argument = arguments_before_file_argument

    def arguments_before_file_argument(self) -> list:
        return self._arguments_before_file_argument


class TestCaseFileArgumentArrangementWithTestActor(TestCaseFileArgumentArrangement):
    def __init__(self,
                 test_case_contents: str = '',
                 arguments_before_file_argument: iter = ()):
        super().__init__(test_case_contents, arguments_before_file_argument)

    def arguments_before_file_argument(self) -> list:
        return arguments_for_test_interpreter_and_more_tuple(self._arguments_before_file_argument)


class SubProcessResultExpectation:
    def apply(self,
              put: unittest.TestCase,
              actual: SubProcessResultInfo):
        raise NotImplementedError()


def run_test(arrangement: TestCaseFileArgumentArrangement,
             expectation: SubProcessResultExpectation,
             main_program_runner: MainProgramRunner,
             put: unittest.TestCase):
    with tmp_file_containing(arrangement.test_case_contents) as test_case_file_path:
        arguments = list(arrangement.arguments_before_file_argument()) + [str(test_case_file_path)]
        sub_process_result = main_program_runner.run(put, arguments)
        sub_process_result_info = SubProcessResultInfo(test_case_file_path, sub_process_result)
        expectation.apply(put, sub_process_result_info)


class ExitCodeAndStdOutputExpectation(SubProcessResultExpectation):
    def __init__(self,
                 exit_code: int=None,
                 std_out: str=None,
                 std_err: str=None):
        self.exit_code = exit_code
        self.std_out = std_out
        self.std_err = std_err

    def apply(self,
              put: unittest.TestCase,
              actual: SubProcessResultInfo):
        if self.exit_code is not None:
            put.assertEqual(self.exit_code,
                            actual.sub_process_result.exitcode,
                            'Exit code')
        if self.std_out is not None:
            put.assertEqual(self.std_out,
                            actual.sub_process_result.stdout,
                            'stdout')
        if self.std_err is not None:
            put.assertEqual(self.std_err,
                            actual.sub_process_result.stderr,
                            'stderr')


def invalid_usage() -> SubProcessResultExpectation:
    return ExitCodeAndStdOutputExpectation(exit_code=EXIT_INVALID_USAGE,
                                           std_out='')


class TestCaseBase(unittest.TestCase):
    def __init__(self, main_program_runner: MainProgramRunner):
        super().__init__()
        self.main_program_runner = main_program_runner

    def runTest(self):
        run_test(self._arrangement(),
                 self._expectation(),
                 self.main_program_runner,
                 self)

    def _arrangement(self) -> TestCaseFileArgumentArrangement:
        raise NotImplementedError()

    def _expectation(self) -> SubProcessResultExpectation:
        raise NotImplementedError()

    def shortDescription(self):
        return str(type(self)) + '/' + self.main_program_runner.description_for_test_name()
