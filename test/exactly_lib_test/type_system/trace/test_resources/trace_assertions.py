import unittest
from typing import Sequence

from exactly_lib.type_system.trace.trace import Detail, Node, PreFormattedStringDetail, StringDetail, DetailVisitor
from exactly_lib.util.strings import ToStringObject
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase, \
    MessageBuilder
from exactly_lib_test.util.test_resources import to_string_assertions as asrt_to_string


def matches_node(header: ValueAssertion[str] = asrt.anything_goes(),
                 data: ValueAssertion = asrt.anything_goes(),
                 details: ValueAssertion[Sequence[Detail]] = asrt.anything_goes(),
                 children: ValueAssertion[Sequence[Node]] = asrt.anything_goes()) -> ValueAssertion[Node]:
    return _MatchesNode(header, data, details, children)


def is_string_detail(to_string_object: ValueAssertion[ToStringObject] = asrt.anything_goes(),
                     ) -> ValueAssertion[Detail]:
    return asrt.is_instance_with__many(
        StringDetail,
        [
            asrt.sub_component('string',
                               StringDetail.string.fget,
                               asrt.and_([
                                   asrt_to_string.matches(asrt.anything_goes()),
                                   to_string_object,
                               ])
                               ),
        ],
    )


def is_pre_formatted_string_detail(to_string_object: ValueAssertion[ToStringObject] = asrt.anything_goes(),
                                   string_is_line_ended: ValueAssertion[bool] = asrt.anything_goes(),
                                   ) -> ValueAssertion[Detail]:
    return asrt.is_instance_with__many(
        PreFormattedStringDetail,
        [
            asrt.sub_component('to_string_object',
                               PreFormattedStringDetail.object_with_to_string.fget,
                               to_string_object,
                               ),
            asrt.sub_component('string_is_line_ended',
                               PreFormattedStringDetail.string_is_line_ended.fget,
                               asrt.is_instance_with(bool, string_is_line_ended),
                               ),
        ],
    )


def is_any_detail() -> ValueAssertion[Detail]:
    return _IS_ANY_DETAIL


class _IsAnyDetail(asrt.ValueAssertionBase[Detail]):

    def _apply(self,
               put: unittest.TestCase,
               value: Detail,
               message_builder: MessageBuilder):
        put.assertIsInstance(value,
                             Detail,
                             message_builder.apply('object type'))
        assert isinstance(value, Detail)
        self._is_known_sub_class(put, value, message_builder)

        detail_checker = _DetailChecker(put)
        value.accept(detail_checker)

    @staticmethod
    def _is_known_sub_class(put: unittest.TestCase,
                            value: Detail,
                            message_builder: MessageBuilder):
        if isinstance(value, StringDetail):
            return
        if isinstance(value, PreFormattedStringDetail):
            return
        msg = 'Not a know sub class of {}: {}'.format(Detail, value)
        put.fail(message_builder.apply(msg))


class _DetailChecker(DetailVisitor[None]):
    def __init__(self, put: unittest.TestCase):
        self._put = put

    def visit_pre_formatted_string(self, x: PreFormattedStringDetail) -> None:
        is_pre_formatted_string_detail().apply_without_message(self._put, x)

    def visit_string(self, x: StringDetail) -> None:
        is_string_detail().apply_without_message(self._put, x)


_IS_ANY_DETAIL = _IsAnyDetail()


class _MatchesNode(ValueAssertionBase[Node]):
    _HEADER_IS_STR = asrt.sub_component('header', Node.header.fget, asrt.is_instance(str))
    _IS_SEQUENCE_OF_DETAIL = asrt.every_element('details', is_any_detail())

    def __init__(self,
                 header: ValueAssertion[str],
                 data: ValueAssertion,
                 details: ValueAssertion[Sequence[Detail]],
                 children: ValueAssertion[Sequence[Node]]):
        self._header = header
        self._data = data
        self._details = details
        self._children = children

    def _apply(self,
               put: unittest.TestCase,
               value: Node,
               message_builder: MessageBuilder):
        self._assert_object_types(put, value, message_builder)

        self._header.apply(put,
                           value.header,
                           message_builder.for_sub_component('header'))

        self._data.apply(put,
                         value.data,
                         message_builder.for_sub_component('data'))

        self._details.apply(put,
                            value.details,
                            message_builder.for_sub_component('details'))

        self._children.apply(put,
                             value.children,
                             message_builder.for_sub_component('children'))

    def _assert_object_types(self,
                             put: unittest.TestCase,
                             value: Node,
                             message_builder: MessageBuilder):
        put.assertIsInstance(value,
                             Node,
                             message_builder.apply('Node object type'))
        self._HEADER_IS_STR.apply(put, value, message_builder)
        self._IS_SEQUENCE_OF_DETAIL.apply(put, value.details, message_builder)
        asrt.every_element('children', matches_node()).apply(put, value.children, message_builder)
