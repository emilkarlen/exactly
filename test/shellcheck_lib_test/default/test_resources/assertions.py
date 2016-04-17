import os

from shellcheck_lib.cli.cli_environment import exit_values
from shellcheck_lib_test.test_resources import value_assertion as va
from shellcheck_lib_test.test_resources.process import SubProcessResult, SubProcessResultInfo


def process_result_for_exit_value(exit_value: exit_values.ExitValue) -> va.ValueAssertion:
    return assertion_on_process_result(
        va.And([
            va.sub_component('exit code',
                             SubProcessResult.exitcode.fget,
                             va.Equals(exit_value.exit_code)),
            va.sub_component('stdout',
                             SubProcessResult.stdout.fget,
                             va.Equals(exit_value.exit_identifier + os.linesep)),
        ])
    )


def process_result_for_exit_code(exit_code: int) -> va.ValueAssertion:
    return assertion_on_process_result(
        va.sub_component('exit code',
                         SubProcessResult.exitcode.fget,
                         va.Equals(exit_code)),
    )


def assertion_on_process_result(assertion: va.ValueAssertion) -> va.ValueAssertion:
    """
    :type assertion: A ValueAssertion on a SubProcessResult.
    """
    return va.sub_component(
        'sub process result',
        SubProcessResultInfo.sub_process_result.fget,
        assertion,
    )