import unittest
from typing import Sequence, Any

from exactly_lib.type_system.trace.trace import Detail, Node, PreFormattedStringDetail, StringDetail, DetailVisitor
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase, \
    MessageBuilder


def matches_node(header: ValueAssertion[str] = asrt.anything_goes(),
                 data: ValueAssertion = asrt.anything_goes(),
                 details: ValueAssertion[Sequence[Detail]] = asrt.anything_goes(),
                 children: ValueAssertion[Sequence[Node]] = asrt.anything_goes()) -> ValueAssertion[Node]:
    return _MatchesNode(header, data, details, children)


class _MatchesNode(ValueAssertionBase[Node]):
    _HEADER_IS_STR = asrt.sub_component('header', Node.header.fget, asrt.is_instance(str))
    _IS_SEQUENCE_OF_DETAIL = asrt.every_element('details', asrt.is_instance(Detail))
    _IS_SEQUENCE_OF_NODE = asrt.every_element('children', asrt.is_instance(Node))

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
        self._IS_SEQUENCE_OF_NODE.apply(put, value.children, message_builder)


def is_string_detail(string: ValueAssertion[str] = asrt.anything_goes(),
                     ) -> ValueAssertion[Detail]:
    return asrt.is_instance_with__many(
        StringDetail,
        [
            asrt.sub_component('string',
                               StringDetail.string.fget,
                               asrt.is_instance_with(str, string)
                               ),
        ],
    )


def is_pre_formatted_string_detail(object_with_to_string: ValueAssertion[Any] = asrt.anything_goes(),
                                   string_is_line_ended: ValueAssertion[bool] = asrt.anything_goes(),
                                   ) -> ValueAssertion[Detail]:
    return asrt.is_instance_with__many(
        PreFormattedStringDetail,
        [
            asrt.sub_component('object_with_to_string',
                               PreFormattedStringDetail.object_with_to_string.fget,
                               object_with_to_string,
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

        detail_checker = DetailChecker(put)
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


class DetailChecker(DetailVisitor[None]):
    def __init__(self, put: unittest.TestCase):
        self._put = put

    def visit_pre_formatted_string(self, x: PreFormattedStringDetail) -> None:
        is_pre_formatted_string_detail().apply_without_message(self._put, x)

    def visit_string(self, x: StringDetail) -> None:
        is_string_detail().apply_without_message(self._put, x)


_IS_ANY_DETAIL = _IsAnyDetail()
