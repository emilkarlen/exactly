import unittest

from exactly_lib.test_case_utils.err_msg2 import trace_rendering as sut
from exactly_lib.type_system.trace.trace import Node, StringDetail
from exactly_lib.util.ansi_terminal_color import ForegroundColor
from exactly_lib.util.simple_textstruct import structure as s
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.simple_textstruct.test_resources import structure_assertions as asrt_struct


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestBasicStructure)


class TestBasicStructure(unittest.TestCase):
    def test_node_with_just_header(self):
        # ARRANGE #

        for data in [False, True]:
            with self.subTest(data=data):
                trace = Node('header', data, (), ())

                renderer = sut.BoolTraceRenderer(trace)

                # ACT #

                actual = renderer.render()

                # ASSERT #

                expectation = asrt_struct.matches_major_block__w_plain_properties(
                    minor_blocks=asrt.matches_sequence([
                        asrt_struct.matches_minor_block__w_plain_properties(
                            line_elements=asrt.matches_singleton_sequence(matches_header_line_element(trace)),
                        )
                    ])
                )

                expectation.apply_without_message(self, actual)

    def test_node_with_detail_and_child(self):
        # ARRANGE #

        for child_data in [False, True]:
            with self.subTest(data=child_data):
                child = Node('the child', child_data, (), ())
                detail = StringDetail('the detail')
                trace = Node('the root', False, [detail], [child])

                renderer = sut.BoolTraceRenderer(trace)

                # ACT #

                actual = renderer.render()

                # ASSERT #

                expectation = asrt_struct.matches_major_block__w_plain_properties(
                    minor_blocks=asrt.matches_sequence([
                        asrt_struct.matches_minor_block__w_plain_properties(
                            line_elements=asrt.matches_sequence([
                                matches_header_line_element(trace),
                                matches_string_detail_line_element(detail, level=1),
                            ]),
                        ),
                        asrt_struct.matches_minor_block(
                            line_elements=asrt.matches_singleton_sequence(matches_header_line_element(child)),
                            properties=asrt_struct.equals_element_properties(expected_child_properties(level=1)),
                        ),
                    ])
                )

                expectation.apply_without_message(self, actual)

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

                        trace = Node('the root', root_data, details, children)

                        renderer = sut.BoolTraceRenderer(trace)

                        # ACT #

                        actual = renderer.render()

                        # ASSERT #

                        expectation = asrt_struct.matches_major_block__w_plain_properties(
                            minor_blocks=asrt.matches_sequence([
                                asrt_struct.matches_minor_block__w_plain_properties(
                                    line_elements=asrt.matches_sequence([
                                        matches_header_line_element(trace),
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

                        expectation.apply_without_message(self, actual)

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
                        trace = Node('the root', root_data, [], [child_1])

                        renderer = sut.BoolTraceRenderer(trace)

                        # ACT #

                        actual = renderer.render()

                        # ASSERT #

                        expectation = asrt_struct.matches_major_block__w_plain_properties(
                            minor_blocks=asrt.matches_sequence([
                                asrt_struct.matches_minor_block__w_plain_properties(
                                    line_elements=asrt.matches_singleton_sequence(matches_header_line_element(trace)),
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

                        expectation.apply_without_message(self, actual)


def matches_header_line_element(node: Node[bool]) -> ValueAssertion[s.LineElement]:
    return asrt_struct.matches_line_element(
        line_object=asrt_struct.is_string__not_line_ended(asrt.equals(_expected_header_line(node))),
        properties=matches_header_properties(node),
    )


def matches_string_detail_line_element(detail: StringDetail, level: int) -> ValueAssertion[s.LineElement]:
    return asrt_struct.matches_line_element(
        line_object=asrt_struct.is_string__not_line_ended(asrt.equals(detail.string)),
        properties=asrt_struct.equals_element_properties(expected_detail_properties(level=level)),
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
    return ' '.join([node.header,
                     '(' + bool_val_str + ')'])


def _expected_header_properties(node: Node[bool]) -> s.ElementProperties:
    return s.ElementProperties(
        0,
        _expected_header_color(node),
        None,
    )


def _expected_header_color(node: Node[bool]) -> ForegroundColor:
    return (
        ForegroundColor.GREEN
        if node.data
        else
        ForegroundColor.RED
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
