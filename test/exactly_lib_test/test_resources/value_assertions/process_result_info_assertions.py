from exactly_lib.common.exit_value import ExitValue
from exactly_lib_test.test_resources.process import SubProcessResultInfo, SubProcessResult
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def process_result_for_exit_value(exit_value: ExitValue) -> ValueAssertion[SubProcessResultInfo]:
    return assertion_on_process_result(pr.is_result_for_exit_value(exit_value))


def is_process_result_for_exit_code(exit_code: int) -> ValueAssertion[SubProcessResultInfo]:
    return assertion_on_process_result(pr.is_result_for_exit_code(exit_code))


def assertion_on_process_result(assertion: ValueAssertion[SubProcessResult]
                                ) -> ValueAssertion[SubProcessResultInfo]:
    return asrt.sub_component(
        'sub process result',
        SubProcessResultInfo.sub_process_result.fget,
        assertion,
    )
