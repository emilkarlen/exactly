import unittest
from typing import Sequence

from exactly_lib.type_system.trace.trace import Detail, Node
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
