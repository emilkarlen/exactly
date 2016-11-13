from exactly_lib.common.exit_value import ExitValue
from exactly_lib_test.test_resources.process import SubProcessResultInfo
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


def process_result_for_exit_value(exit_value: ExitValue) -> va.ValueAssertion:
    """
    :rtype: A ValueAssertion on a SubProcessResultInfo.
    """
    return assertion_on_process_result(pr.is_result_for_exit_value(exit_value))


def is_process_result_for_exit_code(exit_code: int) -> va.ValueAssertion:
    """
    :rtype: A ValueAssertion on a SubProcessResultInfo.
    """
    return assertion_on_process_result(pr.is_result_for_exit_code(exit_code))


def assertion_on_process_result(assertion: va.ValueAssertion) -> va.ValueAssertion:
    """
    :type assertion: A ValueAssertion on a SubProcessResult.
    :rtype: A ValueAssertion on a SubProcessResultInfo.
    """
    return va.sub_component(
        'sub process result',
        SubProcessResultInfo.sub_process_result.fget,
        assertion,
    )
