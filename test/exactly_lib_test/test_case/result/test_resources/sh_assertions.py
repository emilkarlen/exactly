import unittest
from typing import Any

from exactly_lib.test_case.result import sh
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def is_success() -> ValueAssertion[sh.SuccessOrHardError]:
    return _IsSuccess()


class _IsSuccess(ValueAssertion[sh.SuccessOrHardError]):
    def __init__(self):
        pass

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        put.assertIsInstance(value, sh.SuccessOrHardError)
        if not value.is_success:
            put.fail('\n'.join([
                'Expected: success',
                'Actual  : hard_error: ' + str(value.failure_message)
            ]))


def is_hard_error(assertion_on_error_message: ValueAssertion = asrt.anything_goes()
                  ) -> ValueAssertion[sh.SuccessOrHardError]:
    return is_sh_and(asrt.And([
        asrt.sub_component('is_hard_error',
                           sh.SuccessOrHardError.is_hard_error.fget,
                           asrt.equals(True,
                                       'Status is expected to be hard-error')),
        asrt.sub_component('error message',
                           sh.SuccessOrHardError.failure_message.fget,
                           assertion_on_error_message)
    ]))


def is_sh_and(assertion: ValueAssertion[sh.SuccessOrHardError]) -> ValueAssertion[Any]:
    return asrt.is_instance_with(sh.SuccessOrHardError, assertion)
