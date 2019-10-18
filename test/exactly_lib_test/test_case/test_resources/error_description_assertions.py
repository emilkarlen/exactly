import unittest
from typing import Optional

from exactly_lib.common.report_rendering.text_doc import MinorTextRenderer
from exactly_lib.test_case import error_description as err_descr
from exactly_lib.test_case.error_description import ErrorDescription, ExternalProcessError, ErrorDescriptionVisitor, \
    ErrorDescriptionOfExternalProcessError, ErrorDescriptionOfException, ErrorDescriptionOfMessage
from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, MessageBuilder
from exactly_lib_test.util.simple_textstruct.test_resources import renderer_assertions as asrt_renderer


def matches_message(message: ValueAssertion[MinorTextRenderer] = asrt.anything_goes()
                    ) -> ValueAssertion[ErrorDescription]:
    return asrt.is_none_or_instance_with(
        err_descr.ErrorDescriptionOfMessage,
        asrt.sub_component_many(
            'message',
            err_descr.ErrorDescriptionOfMessage.message.fget,
            [
                asrt_renderer.is_renderer_of_major_blocks(),
                message,
            ],
        )
    )


def matches_exception(exception: ValueAssertion[Exception] = asrt.anything_goes(),
                      message: Optional[ValueAssertion[MinorTextRenderer]] = asrt.anything_goes()
                      ) -> ValueAssertion[ErrorDescription]:
    return asrt.is_none_or_instance_with__many(
        err_descr.ErrorDescriptionOfException,
        [
            asrt.sub_component_many(
                'message',
                err_descr.ErrorDescriptionOfException.message.fget,
                [
                    asrt.is_none_or_instance_with(SequenceRenderer, asrt_renderer.is_renderer_of_major_blocks()),
                    message,
                ],
            ),
            asrt.sub_component(
                'exception',
                err_descr.ErrorDescriptionOfException.exception.fget,
                asrt.is_instance_with(
                    Exception,
                    exception,
                )
            ),
        ],
    )


def matches_external_process(external_process_error: ValueAssertion[ExternalProcessError] = asrt.anything_goes(),
                             message: Optional[ValueAssertion[MinorTextRenderer]] = asrt.anything_goes()
                             ) -> ValueAssertion[ErrorDescription]:
    return asrt.is_none_or_instance_with__many(
        err_descr.ErrorDescriptionOfExternalProcessError,
        [
            asrt.sub_component_many(
                'message',
                err_descr.ErrorDescriptionOfExternalProcessError.message.fget,
                [
                    asrt.is_none_or_instance_with(SequenceRenderer, asrt_renderer.is_renderer_of_major_blocks()),
                    message,
                ],
            ),
            asrt.sub_component(
                'external_process_error',
                err_descr.ErrorDescriptionOfExternalProcessError.external_process_error.fget,
                asrt.is_instance_with(
                    ExternalProcessError,
                    external_process_error,
                )
            ),
        ],
    )


def is_any_error_description() -> ValueAssertion[ErrorDescription]:
    return _AnyErrorDescriptionAssertion()


class _AnyErrorDescriptionAssertion(asrt.ValueAssertionBase[ErrorDescription]):

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: MessageBuilder):
        put.assertIsInstance(
            value,
            ErrorDescription,
            message_builder.apply('object type')
        )

        assert isinstance(value, ErrorDescription)  # Type info for IDE

        checker = _CheckAnyErrorDescription(put, message_builder)

        try:
            checker.visit(value)
        except TypeError:
            put.fail('Not a known sub class of {}: {}'.format(
                ErrorDescription,
                value
            ))


class _CheckAnyErrorDescription(ErrorDescriptionVisitor[None]):
    def __init__(self,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder):
        self._put = put
        self._message_builder = message_builder

    def _visit_message(self, error_description: ErrorDescriptionOfMessage) -> None:
        matches_message().apply(
            self._put,
            error_description,
            self._message_builder.for_sub_component('ErrorDescriptionOfMessage')
        )

    def _visit_exception(self, error_description: ErrorDescriptionOfException) -> None:
        matches_exception().apply(
            self._put,
            error_description,
            self._message_builder.for_sub_component('ErrorDescriptionOfException')
        )

    def _visit_external_process_error(self, error_description: ErrorDescriptionOfExternalProcessError) -> None:
        matches_external_process().apply(
            self._put,
            error_description,
            self._message_builder.for_sub_component('ErrorDescriptionOfExternalProcessError')
        )
