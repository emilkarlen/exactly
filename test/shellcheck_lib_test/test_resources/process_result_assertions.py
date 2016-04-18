import os

from shellcheck_lib.cli.cli_environment import exit_values
from shellcheck_lib_test.test_resources import value_assertion as va
from shellcheck_lib_test.test_resources.process import SubProcessResult


def is_result_for_exit_value(exit_value: exit_values.ExitValue) -> va.ValueAssertion:
    """
    :rtype: A ValueAssertion on a SubProcessResult.
    """
    return va.And([
        va.sub_component('exit code',
                         SubProcessResult.exitcode.fget,
                         va.Equals(exit_value.exit_code)),
        va.sub_component('stdout',
                         SubProcessResult.stdout.fget,
                         va.Equals(exit_value.exit_identifier + os.linesep)),
    ])


def is_result_for_exit_code(exit_code: int) -> va.ValueAssertion:
    """
    :rtype: A ValueAssertion on a SubProcessResult.
    """
    return va.sub_component('exit code',
                            SubProcessResult.exitcode.fget,
                            va.Equals(exit_code))
