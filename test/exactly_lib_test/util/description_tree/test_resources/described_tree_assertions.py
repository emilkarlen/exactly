import unittest
from typing import Sequence, Any

from exactly_lib.util.description_tree.tree import Detail, Node, PreFormattedStringDetail, StringDetail, DetailVisitor, \
    HeaderAndValueDetail, TreeDetail, NODE_DATA, IndentedDetail
from exactly_lib.util.str_.str_constructor import ToStringObject
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, AssertionBase, \
    MessageBuilder
from exactly_lib_test.util.test_resources import to_string_assertions as asrt_to_string


def matches_node(header: Assertion[str] = asrt.anything_goes(),
                 data: Assertion = asrt.anything_goes(),
                 details: Assertion[Sequence[Detail]] = asrt.anything_goes(),
                 children: Assertion[Sequence[Node]] = asrt.anything_goes()) -> Assertion[Node]:
    return _MatchesNode(header, data, details, children)


def equals_node(expected: Node) -> Assertion[Node]:
    return matches_node(
        header=asrt.equals(expected.header),
        data=asrt.equals(expected.data),
        details=equals_details(expected.details),
        children=equals_nodes(expected.children),
    )


def equals_nodes(expected: Sequence[Node]) -> Assertion[Sequence[Node]]:
    return asrt.matches_sequence([
        equals_node(n)
        for n in expected
    ])


def header_data_and_children_equal_as(node: Node[NODE_DATA]) -> Assertion[Node[NODE_DATA]]:
    return matches_node(
        header=asrt.equals(node.header),
        data=asrt.equals(node.data),
        children=asrt.matches_sequence([
            header_data_and_children_equal_as(child)
            for child in node.children
        ])
    )


def equals_detail(expected: Detail) -> Assertion[Detail]:
    return _EqualsDetailAssertion(expected)


def equals_details(expected: Sequence[Detail]) -> Assertion[Sequence[Detail]]:
    return asrt.matches_sequence([
        equals_detail(d)
        for d in expected
    ])


def is_string_detail(to_string_object: Assertion[ToStringObject] = asrt.anything_goes(),
                     ) -> Assertion[Detail]:
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


def is_pre_formatted_string_detail(to_string_object: Assertion[ToStringObject] = asrt.anything_goes(),
                                   string_is_line_ended: Assertion[bool] = asrt.anything_goes(),
                                   ) -> Assertion[Detail]:
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


def is_header_and_value_detail(header: Assertion[ToStringObject] = asrt.anything_goes(),
                               values: Assertion[Sequence[Detail]] = asrt.is_sequence_of(asrt.is_instance(Detail)),
                               ) -> Assertion[Detail]:
    return asrt.is_instance_with__many(
        HeaderAndValueDetail,
        [
            asrt.sub_component('header',
                               HeaderAndValueDetail.header.fget,
                               asrt.is_not_none_and(header),
                               ),
            asrt.sub_component('values',
                               HeaderAndValueDetail.values.fget,
                               asrt.is_not_none_and(values),
                               ),
        ],
    )


def is_indented_detail(details: Assertion[Sequence[Detail]] = asrt.is_sequence_of(asrt.is_instance(Detail)),
                       ) -> Assertion[Detail]:
    return asrt.is_instance_with__many(
        IndentedDetail,
        [
            asrt.sub_component('values',
                               IndentedDetail.details.fget,
                               asrt.is_not_none_and(details),
                               ),
        ],
    )


def is_tree_detail(tree: Assertion[Node[Any]] = asrt.anything_goes(),
                   ) -> Assertion[Detail]:
    return asrt.is_instance_with__many(
        TreeDetail,
        [
            asrt.sub_component('tree',
                               TreeDetail.tree.fget,
                               asrt.is_not_none_and(asrt.and_([_MatchesNode(), tree])),
                               ),
        ],
    )


def is_any_detail() -> Assertion[Detail]:
    return _IS_ANY_DETAIL


class _IsAnyDetail(asrt.AssertionBase[Detail]):
    def _apply(self,
               put: unittest.TestCase,
               value: Detail,
               message_builder: MessageBuilder):
        put.assertIsInstance(value,
                             Detail,
                             message_builder.apply('object type'))
        assert isinstance(value, Detail)
        self._is_known_sub_class(put, value, message_builder)

        detail_checker = _IsValidDetail(put, message_builder)
        value.accept(detail_checker)

    @staticmethod
    def _is_known_sub_class(put: unittest.TestCase,
                            value: Detail,
                            message_builder: MessageBuilder):
        if isinstance(value, StringDetail):
            return
        if isinstance(value, PreFormattedStringDetail):
            return
        if isinstance(value, HeaderAndValueDetail):
            return
        if isinstance(value, TreeDetail):
            return
        if isinstance(value, IndentedDetail):
            return
        msg = 'Not a know sub class of {}: {}'.format(Detail, value)
        put.fail(message_builder.for_sub_component('Detail class').apply(msg))


_IS_ANY_DETAIL = _IsAnyDetail()


class _IsValidDetail(DetailVisitor[None]):
    def __init__(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder):
        self._put = put
        self._message_builder = message_builder

    def visit_pre_formatted_string(self, x: PreFormattedStringDetail) -> None:
        is_pre_formatted_string_detail().apply(self._put, x, self._message_builder)

    def visit_string(self, x: StringDetail) -> None:
        is_string_detail().apply(self._put, x, self._message_builder)

    def visit_header_and_value(self, x: HeaderAndValueDetail) -> None:
        is_header_and_value_detail().apply(self._put, x, self._message_builder)

    def visit_indented(self, x: IndentedDetail) -> None:
        is_indented_detail().apply(self._put, x, self._message_builder)

    def visit_tree(self, x: TreeDetail) -> None:
        is_tree_detail().apply(self._put, x, self._message_builder)


class _EqualsDetailChecker(DetailVisitor[None]):
    def __init__(self,
                 actual: Detail,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder):
        self._actual = actual
        self._put = put
        self._message_builder = message_builder

    def visit_pre_formatted_string(self, expected: PreFormattedStringDetail) -> None:
        expectation = is_pre_formatted_string_detail(
            to_string_object=asrt_to_string.equals(str(expected.object_with_to_string)),
            string_is_line_ended=asrt.equals(expected.string_is_line_ended),
        )
        expectation.apply(self._put, self._actual, self._message_builder)

    def visit_string(self, expected: StringDetail) -> None:
        expectation = is_string_detail(
            to_string_object=asrt_to_string.equals(str(expected.string))
        )
        expectation.apply(self._put, self._actual, self._message_builder)

    def visit_header_and_value(self, expected: HeaderAndValueDetail) -> None:
        expectation = is_header_and_value_detail(
            header=asrt_to_string.equals(str(expected.header)),
            values=equals_details(expected.values),
        )
        expectation.apply(self._put, self._actual, self._message_builder)

    def visit_indented(self, expected: IndentedDetail) -> None:
        expectation = is_indented_detail(
            equals_details(expected.details)
        )
        expectation.apply(self._put, self._actual, self._message_builder)

    def visit_tree(self, expected: TreeDetail) -> None:
        expectation = is_tree_detail(
            equals_node(expected.tree)
        )
        expectation.apply(self._put, self._actual, self._message_builder)


class _EqualsDetailAssertion(AssertionBase[Detail]):
    def __init__(self, expected: Detail):
        self._expected = expected

    def _apply(self,
               put: unittest.TestCase,
               actual,
               message_builder: MessageBuilder):
        checker = _EqualsDetailChecker(actual, put, message_builder)
        self._expected.accept(checker)


class _MatchesNode(AssertionBase[Node]):
    _HEADER_IS_STR = asrt.sub_component('header', Node.header.fget, asrt.is_instance(str))
    _IS_SEQUENCE_OF_DETAIL = asrt.every_element('details', is_any_detail())

    def __init__(self,
                 header: Assertion[str] = asrt.anything_goes(),
                 data: Assertion = asrt.anything_goes(),
                 details: Assertion[Sequence[Detail]] = asrt.anything_goes(),
                 children: Assertion[Sequence[Node]] = asrt.anything_goes(),
                 ):
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
