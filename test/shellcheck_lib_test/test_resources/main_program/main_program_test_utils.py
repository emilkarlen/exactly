import os

from shellcheck_lib.cli.cli_environment.exit_value import ExitValue
from shellcheck_lib_test.test_resources.process import ExpectedSubProcessResult


def process_result_for(exit_value: ExitValue) -> ExpectedSubProcessResult:
    return ExpectedSubProcessResult(exitcode=exit_value.exit_code,
                                    stdout=exit_value.exit_identifier + os.linesep)
