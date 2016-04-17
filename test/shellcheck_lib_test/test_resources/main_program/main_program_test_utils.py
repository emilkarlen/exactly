import os

from shellcheck_lib.cli.cli_environment import exit_values
from shellcheck_lib_test.test_resources.process import ExpectedSubProcessResult


def process_result_for(exit_value: exit_values.ExitValue) -> ExpectedSubProcessResult:
    return ExpectedSubProcessResult(exitcode=exit_value.exit_code,
                                    stdout=exit_value.exit_identifier + os.linesep)