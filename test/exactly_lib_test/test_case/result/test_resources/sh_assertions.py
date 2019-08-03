import unittest
from typing import Any

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.result import sh
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder, ValueAssertionBase
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def is_success() -> ValueAssertion[sh.SuccessOrHardError]:
    return _IsSuccess()


def is_hard_error(assertion_on_error_message: ValueAssertion[TextRenderer] =
                  asrt_text_doc.is_any_text()
                  ) -> ValueAssertion[sh.SuccessOrHardError]:
    return is_sh_and(asrt.And([
        asrt.sub_component('is_hard_error',
                           sh.SuccessOrHardError.is_hard_error.fget,
                           asrt.equals(True,
                                       'Status is expected to be hard-error')),
        asrt.sub_component('failure_message',
                           sh.SuccessOrHardError.failure_message.fget,
                           assertion_on_error_message)
    ]))


def is_sh_and(assertion: ValueAssertion[sh.SuccessOrHardError]) -> ValueAssertion[Any]:
    return asrt.is_instance_with(sh.SuccessOrHardError, assertion)


class _IsSuccess(ValueAssertionBase[sh.SuccessOrHardError]):
    def __init__(self):
        pass

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: MessageBuilder):
        put.assertIsInstance(value, sh.SuccessOrHardError)
        if not value.is_success:
            from exactly_lib.util.simple_textstruct.file_printer_output import to_string
            put.fail('\n'.join([
                'Expected: success',
                'Actual  : hard_error: ' + to_string.major_blocks(value.failure_message.render())
            ]))
