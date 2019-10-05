import unittest

from exactly_lib.util import strings
from exactly_lib.util.ansi_terminal_color import ForegroundColor, FontStyle
from exactly_lib.util.description_tree import rendering as sut
from exactly_lib.util.description_tree.rendering import RenderingConfiguration
from exactly_lib.util.description_tree.tree import Node, StringDetail, PreFormattedStringDetail
from exactly_lib.util.simple_textstruct import structure as s
from exactly_lib.util.simple_textstruct.structure import ElementProperties, TEXT_STYLE__NEUTRAL, Indentation, \
    INDENTATION__NEUTRAL, TextStyle
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
        for data in [False, True]:
            with self.subTest(data=data):
                root = Node('header', data, (), ())

                # EXPECTATION #

                expectation = asrt_struct.matches_major_block__w_plain_properties(
                    minor_blocks=asrt.matches_sequence([
                        asrt_struct.matches_minor_block(
                            line_elements=asrt.matches_singleton_sequence(matches_header_line_element(root)),
                            properties=matches_node_properties(depth=0),
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
                        asrt_struct.matches_minor_block(
                            line_elements=asrt.matches_sequence([
                                matches_header_line_element(root),
                                matches_string_detail_line_element(detail, depth=0),
                            ]),
                            properties=matches_node_properties(depth=0),
                        ),
                        asrt_struct.matches_minor_block(
                            line_elements=asrt.matches_singleton_sequence(
                                matches_header_line_element(child)
                            ),
                            properties=matches_node_properties(depth=1),
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
                                asrt_struct.matches_minor_block(
                                    line_elements=asrt.matches_sequence([
                                        matches_header_line_element(root),
                                        matches_string_detail_line_element(detail_1, depth=0),
                                        matches_string_detail_line_element(detail_2, depth=0),
                                    ]),
                                    properties=matches_node_properties(depth=0),
                                ),
                                asrt_struct.matches_minor_block(
                                    line_elements=
                                    asrt.matches_singleton_sequence(
                                        matches_header_line_element(child_1)
                                    ),
                                    properties=
                                    matches_node_properties(depth=1),
                                ),
                                asrt_struct.matches_minor_block(
                                    line_elements=
                                    asrt.matches_singleton_sequence(matches_header_line_element(child_2)),
                                    properties=
                                    matches_node_properties(depth=1),
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
                                asrt_struct.matches_minor_block(
                                    line_elements=asrt.matches_singleton_sequence(matches_header_line_element(root)),
                                    properties=matches_node_properties(depth=0)
                                ),
                                asrt_struct.matches_minor_block(
                                    line_elements=asrt.matches_singleton_sequence(matches_header_line_element(child_1)),
                                    properties=matches_node_properties(depth=1)),
                                asrt_struct.matches_minor_block(
                                    line_elements=asrt.matches_singleton_sequence(
                                        matches_header_line_element(child_11)
                                    ),
                                    properties=matches_node_properties(depth=2),
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
                    matches_string_detail_line_element(detail, depth=0),
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
                        matches_pre_formatted_string_detail_line_element(detail, depth=0),
                    )

                    # ACT & ASSERT #

                    _check(self, root, expectation)


def _check(put: unittest.TestCase,
           node: Node[bool],
           expectation: ValueAssertion[s.MajorBlock],
           ):
    renderer = sut.TreeRenderer(RENDERING_CONFIGURATION, node)

    # ACT #

    block = renderer.render()

    # ASSERT #

    expectation.apply_with_message(put, block, 'from node-renderer')


def _get_header(node: Node[bool]) -> str:
    return ':'.join([str(node.data), node.header])


def _get_header_style(node: Node[bool]) -> ElementProperties:
    return (
        _HEADER_PROPERTIES_FOR_T
        if node.data
        else
        _HEADER_PROPERTIES_FOR_F
    )


RENDERING_CONFIGURATION = RenderingConfiguration(
    _get_header,
    _get_header_style,
    '<DETAIL-INDENT>',
)


def matches_trace_with_just_single_detail(trace: Node[bool],
                                          detail: ValueAssertion[s.LineElement],
                                          ) -> ValueAssertion[s.MajorBlock]:
    return asrt_struct.matches_major_block__w_plain_properties(
        minor_blocks=asrt.matches_singleton_sequence(
            asrt_struct.matches_minor_block(
                line_elements=asrt.matches_sequence([
                    matches_header_line_element(trace),
                    detail,
                ]),
                properties=matches_node_properties(depth=0),
            ))
    )


def matches_header_line_element(node: Node[bool]) -> ValueAssertion[s.LineElement]:
    return asrt_struct.matches_line_element(
        line_object=asrt_struct.is_string__not_line_ended(asrt.equals(_expected_header_line(node))),
        properties=asrt_struct.equals_element_properties(
            _get_header_style(node)
        ),
    )


def matches_string_detail_line_element(detail: StringDetail, depth: int) -> ValueAssertion[s.LineElement]:
    return asrt_struct.matches_line_element(
        line_object=asrt_struct.is_string__not_line_ended(
            asrt.equals(str(detail.string))),
        properties=matches_detail_properties(depth=depth),
    )


def matches_pre_formatted_string_detail_line_element(detail: PreFormattedStringDetail,
                                                     depth: int,
                                                     ) -> ValueAssertion[s.LineElement]:
    return asrt_struct.matches_line_element(
        line_object=asrt_struct.is_pre_formatted_string(
            string=asrt.equals(str(detail.object_with_to_string)),
            string_is_line_ended=asrt.equals(detail.string_is_line_ended),
        ),
        properties=matches_detail_properties(depth=depth),
    )


def matches_header_properties(node: Node[bool]) -> ValueAssertion[s.ElementProperties]:
    return asrt_struct.equals_element_properties(_expected_header_properties(node))


def _expected_header_line(node: Node[bool]) -> str:
    return _get_header(node)


def _expected_header_properties(node: Node[bool]) -> s.ElementProperties:
    return (
        _HEADER_PROPERTIES_FOR_F
        if node.data
        else
        _HEADER_PROPERTIES_FOR_T
    )


def _expected_header_color(node: Node[bool]) -> ForegroundColor:
    return (
        ForegroundColor.BRIGHT_GREEN
        if node.data
        else
        ForegroundColor.BRIGHT_RED
    )


def expected_node_properties(depth: int) -> s.ElementProperties:
    return s.ElementProperties(
        Indentation(depth,
                    ''),
        TEXT_STYLE__NEUTRAL,
    )


def matches_node_properties(depth: int) -> ValueAssertion[s.ElementProperties]:
    return asrt_struct.equals_element_properties(expected_node_properties(depth))


def expected_detail_properties(depth: int) -> s.ElementProperties:
    return s.ElementProperties(
        Indentation(depth + 1,
                    RENDERING_CONFIGURATION.detail_indent),
        TEXT_STYLE__NEUTRAL,
    )


def matches_detail_properties(depth: int) -> ValueAssertion[s.ElementProperties]:
    return asrt_struct.equals_element_properties(expected_detail_properties(depth))


STRING_OBJECT_CASES = [
    NameAndValue('constant',
                 'a string constant',
                 ),
    NameAndValue('must apply str',
                 strings.FormatPositional('{}', 'a string that is generated'),
                 ),
]

_HEADER_PROPERTIES_FOR_F = ElementProperties(INDENTATION__NEUTRAL,
                                             TextStyle(color=ForegroundColor.RED,
                                                       font_style=FontStyle.BOLD),
                                             )
_HEADER_PROPERTIES_FOR_T = ElementProperties(INDENTATION__NEUTRAL,
                                             TextStyle(color=ForegroundColor.GREEN),
                                             )
