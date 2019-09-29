import unittest

from exactly_lib.test_case_utils.err_msg2 import trace_rendering as sut
from exactly_lib.type_system.trace.trace import Node, StringDetail, PreFormattedStringDetail
from exactly_lib.type_system.trace.trace_renderer import NodeRenderer
from exactly_lib.util import strings
from exactly_lib.util.ansi_terminal_color import ForegroundColor
from exactly_lib.util.simple_textstruct import structure as s
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.simple_textstruct.test_resources import structure_assertions as asrt_struct


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestBasicStructure),
        unittest.makeSuite(TestRenderingOfDetail),
    ])


class TestBasicStructure(unittest.TestCase):
    def test_node_with_just_header(self):
        # ARRANGE #
        for string_object_case in STRING_OBJECT_CASES:
            for data in [False, True]:
                with self.subTest(data=data,
                                  string_object=string_object_case.name):
                    root = Node(string_object_case.value, data, (), ())

                    # EXPECTATION #

                    expectation = asrt_struct.matches_major_block__w_plain_properties(
                        minor_blocks=asrt.matches_sequence([
                            asrt_struct.matches_minor_block__w_plain_properties(
                                line_elements=asrt.matches_singleton_sequence(matches_header_line_element(root)),
                            )
                        ])
                    )

                    # ACT & ASSERT #

                    _check(self, root, expectation)

    def test_node_with_detail_and_child(self):
        # ARRANGE #

        for child_data in [False, True]:
            with self.subTest(data=child_data):
                child = Node('the child', child_data, (), ())
                detail = StringDetail('the detail')
                root = Node('the root', False, [detail], [child])

                # EXPECTATION #

                expectation = asrt_struct.matches_major_block__w_plain_properties(
                    minor_blocks=asrt.matches_sequence([
                        asrt_struct.matches_minor_block__w_plain_properties(
                            line_elements=asrt.matches_sequence([
                                matches_header_line_element(root),
                                matches_string_detail_line_element(detail, level=1),
                            ]),
                        ),
                        asrt_struct.matches_minor_block(
                            line_elements=asrt.matches_singleton_sequence(matches_header_line_element(child)),
                            properties=asrt_struct.equals_element_properties(expected_child_properties(level=1)),
                        ),
                    ])
                )

                # ACT & ASSERT #

                _check(self, root, expectation)

    def test_node_with_2_details_and_2_children(self):
        for root_data in [False, True]:
            for child_1_data in [False, True]:
                for child_2_data in [False, True]:
                    with self.subTest(root_data=root_data,
                                      child_1_data=child_1_data,
                                      child_11_data=child_2_data):
                        child_1 = Node('the child 1', child_1_data, (), ())
                        child_2 = Node('the child 2', child_2_data, (), ())
                        children = [child_1, child_2]

                        detail_1 = StringDetail('the detail 1')
                        detail_2 = StringDetail('the detail 2')
                        details = [detail_1, detail_2]

                        root = Node('the root', root_data, details, children)

                        # EXPECTATION #

                        expectation = asrt_struct.matches_major_block__w_plain_properties(
                            minor_blocks=asrt.matches_sequence([
                                asrt_struct.matches_minor_block__w_plain_properties(
                                    line_elements=asrt.matches_sequence([
                                        matches_header_line_element(root),
                                        matches_string_detail_line_element(detail_1, level=1),
                                        matches_string_detail_line_element(detail_2, level=1),
                                    ]),
                                ),
                                asrt_struct.matches_minor_block(
                                    line_elements=
                                    asrt.matches_singleton_sequence(matches_header_line_element(child_1)),
                                    properties=
                                    asrt_struct.equals_element_properties(expected_child_properties(level=1)),
                                ),
                                asrt_struct.matches_minor_block(
                                    line_elements=
                                    asrt.matches_singleton_sequence(matches_header_line_element(child_2)),
                                    properties=
                                    asrt_struct.equals_element_properties(expected_child_properties(level=1)),
                                ),
                            ])
                        )

                        # ACT & ASSERT #

                        _check(self, root, expectation)

    def test_node_with_child_with_child(self):
        # ARRANGE #

        for root_data in [False, True]:
            for child_1_data in [False, True]:
                for child_11_data in [False, True]:
                    with self.subTest(root_data=root_data,
                                      child_1_data=child_1_data,
                                      child_11_data=child_11_data):
                        child_11 = Node('the child 11', child_11_data, (), ())
                        child_1 = Node('the child_1', child_1_data, (), [child_11])
                        root = Node('the root', root_data, [], [child_1])

                        # EXPECTATION #

                        expectation = asrt_struct.matches_major_block__w_plain_properties(
                            minor_blocks=asrt.matches_sequence([
                                asrt_struct.matches_minor_block__w_plain_properties(
                                    line_elements=asrt.matches_singleton_sequence(matches_header_line_element(root)),
                                ),
                                asrt_struct.matches_minor_block(
                                    line_elements=asrt.matches_singleton_sequence(matches_header_line_element(child_1)),
                                    properties=asrt_struct.equals_element_properties(
                                        expected_child_properties(level=1)),
                                ),
                                asrt_struct.matches_minor_block(
                                    line_elements=asrt.matches_singleton_sequence(
                                        matches_header_line_element(child_11)),
                                    properties=asrt_struct.equals_element_properties(
                                        expected_child_properties(level=2)),
                                ),
                            ])
                        )

                        # ACT & ASSERT #

                        _check(self, root, expectation)


class TestRenderingOfDetail(unittest.TestCase):
    def test_string_detail(self):
        # ARRANGE #
        for string_object_case in STRING_OBJECT_CASES:
            with self.subTest(string_object_case.name):
                detail = StringDetail(string_object_case.value)
                root = Node('the root', False, [detail], ())

                # EXPECTATION #

                expectation = matches_trace_with_just_single_detail(
                    root,
                    matches_string_detail_line_element(detail, level=1),
                )

                # ACT & ASSERT #

                _check(self, root, expectation)

    def test_pre_formatted_string_detail(self):
        # ARRANGE #
        for string_object_case in STRING_OBJECT_CASES:
            for string_is_line_ended in [False, True]:
                with self.subTest(string_is_line_ended=string_is_line_ended,
                                  string_type=string_object_case.name):
                    detail = PreFormattedStringDetail(string_object_case.value, string_is_line_ended)

                    root = Node('the root', True, [detail], ())

                    # EXPECTATION #

                    expectation = matches_trace_with_just_single_detail(
                        root,
                        matches_pre_formatted_string_detail_line_element(detail, level=1),
                    )

                    # ACT & ASSERT #

                    _check(self, root, expectation)


def _check(put: unittest.TestCase,
           node: Node[bool],
           expectation: ValueAssertion[s.MajorBlock],
           ):
    renderer_renderer = sut.BoolTraceRenderer(_ConstantRenderer(node))
    renderer = sut.BoolNodeRenderer(node)

    # ACT #

    block__r = renderer.render()
    block__rr = renderer_renderer.render()

    # ASSERT #

    expectation.apply_with_message(put, block__r, 'from node-renderer')
    expectation.apply_with_message(put, block__rr, 'from trace-renderer')


def matches_trace_with_just_single_detail(trace: Node[bool],
                                          detail: ValueAssertion[s.LineElement],
                                          ) -> ValueAssertion[s.MajorBlock]:
    return asrt_struct.matches_major_block__w_plain_properties(
        minor_blocks=asrt.matches_singleton_sequence(
            asrt_struct.matches_minor_block__w_plain_properties(
                line_elements=asrt.matches_sequence([
                    matches_header_line_element(trace),
                    detail,
                ]),
            ))
    )


def matches_header_line_element(node: Node[bool]) -> ValueAssertion[s.LineElement]:
    return asrt_struct.matches_line_element(
        line_object=asrt_struct.is_string__not_line_ended(asrt.equals(_expected_header_line(node))),
        properties=matches_header_properties(node),
    )


def matches_string_detail_line_element(detail: StringDetail, level: int) -> ValueAssertion[s.LineElement]:
    return asrt_struct.matches_line_element(
        line_object=asrt_struct.is_string__not_line_ended(asrt.equals(str(sut.DETAILS_INDENT + str(detail.string)))),
        properties=asrt_struct.equals_element_properties(expected_detail_properties(level=level - 1)),
    )


def matches_pre_formatted_string_detail_line_element(detail: PreFormattedStringDetail,
                                                     level: int,
                                                     ) -> ValueAssertion[s.LineElement]:
    return asrt_struct.matches_line_element(
        line_object=asrt_struct.is_pre_formatted_string(
            string=asrt.equals(str(detail.object_with_to_string)),
            string_is_line_ended=asrt.equals(detail.string_is_line_ended),
        ),
        properties=asrt_struct.equals_element_properties(expected_detail_properties(level=level - 1)),
    )


def matches_header_properties(node: Node[bool]) -> ValueAssertion[s.ElementProperties]:
    return asrt_struct.equals_element_properties(_expected_header_properties(node))


def _expected_header_line(node: Node[bool]) -> str:
    bool_val_str = (
        'T'
        if node.data
        else
        'F'
    )
    return ' '.join([
        '(' + bool_val_str + ')',
        str(node.header),
    ])


def _expected_header_properties(node: Node[bool]) -> s.ElementProperties:
    return s.ElementProperties(
        0,
        _expected_header_color(node),
        None,
    )


def _expected_header_color(node: Node[bool]) -> ForegroundColor:
    return (
        ForegroundColor.BRIGHT_GREEN
        if node.data
        else
        ForegroundColor.BRIGHT_RED
    )


def expected_child_properties(level: int) -> s.ElementProperties:
    return s.ElementProperties(
        level,
        None,
        None,
    )


def expected_detail_properties(level: int) -> s.ElementProperties:
    return s.ElementProperties(
        level,
        None,
        None,
    )


class _ConstantRenderer(NodeRenderer[bool]):
    def __init__(self, constant: Node[bool]):
        self._constant = constant

    def render(self) -> Node[bool]:
        return self._constant


STRING_OBJECT_CASES = [
    NameAndValue('constant',
                 'a string constant',
                 ),
    NameAndValue('must apply str',
                 strings.FormatPositional('{}', 'a string that is generated'),
                 ),
]
