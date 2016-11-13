import os

from exactly_lib.common.exit_value import ExitValue
from exactly_lib_test.test_resources.process import ExpectedSubProcessResult


def process_result_for(exit_value: ExitValue) -> ExpectedSubProcessResult:
    return ExpectedSubProcessResult(exitcode=exit_value.exit_code,
                                    stdout=exit_value.exit_identifier + os.linesep)
