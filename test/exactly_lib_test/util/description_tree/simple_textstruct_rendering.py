import unittest
from typing import Sequence

from exactly_lib.util.ansi_terminal_color import ForegroundColor, FontStyle
from exactly_lib.util.description_tree import simple_textstruct_rendering as sut
from exactly_lib.util.description_tree.simple_textstruct_rendering import RenderingConfiguration
from exactly_lib.util.description_tree.tree import Node, StringDetail, PreFormattedStringDetail, HeaderAndValueDetail, \
    TreeDetail, IndentedDetail
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.simple_textstruct import structure as s
from exactly_lib.util.simple_textstruct.structure import ElementProperties, TEXT_STYLE__NEUTRAL, Indentation, \
    INDENTATION__NEUTRAL, TextStyle
from exactly_lib.util.str_ import str_constructor
from exactly_lib_test.test_resources.test_utils import NIE, NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.util.simple_textstruct.test_resources import structure_assertions as asrt_struct


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestBasicStructure),
        unittest.makeSuite(TestRenderingOfDetail),
        unittest.makeSuite(TestTreeDetail),
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

    def test_header_and_value_detail(self):
        # ARRANGE #
        text_style__non_neutral = TextStyle(font_style=FontStyle.UNDERLINE)
        cases = [
            NIE(
                'without text style',
                TEXT_STYLE__NEUTRAL,
                TEXT_STYLE__NEUTRAL,
            ),
            NIE(
                'with text style',
                text_style__non_neutral,
                text_style__non_neutral,
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                value_detail = StringDetail('the value detail')
                header_and_value_detail = HeaderAndValueDetail('the header', [value_detail], case.input_value)
                root = Node('the root', False, [header_and_value_detail], ())

                # EXPECTATION #

                expectation = matches_trace_with_details(
                    root,
                    [
                        matches_detail_line_element(header_and_value_detail.header,
                                                    depth=0,
                                                    text_style=case.expected_value),
                        matches_string_detail_line_element(value_detail, depth=1),
                    ],
                )

                # ACT & ASSERT #

                _check(self, root, expectation)

    def test_indented_detail(self):
        # ARRANGE #
        details_1 = StringDetail('indented detail 1')
        details_2 = StringDetail('indented detail 2')
        indented_detail = IndentedDetail([details_1, details_2])
        root = Node('the root', False, [indented_detail], ())

        # EXPECTATION #

        expectation = matches_trace_with_details(
            root,
            [
                matches_string_detail_line_element(details_1, depth=1),
                matches_string_detail_line_element(details_2, depth=1),
            ],
        )

        # ACT & ASSERT #

        _check(self, root, expectation)


class TestTreeDetail(unittest.TestCase):
    def test_node_with_no_details_or_children(self):
        # ARRANGE #
        tree_in_detail = Node('the contained tree root', None, (), ())

        text_style__non_neutral = TextStyle(font_style=FontStyle.BOLD)

        header_text_style_cases = [
            NEA(
                'default text style',
                TEXT_STYLE__NEUTRAL,
                TreeDetail(tree_in_detail),
            ),
            NEA(
                'custom text style',
                text_style__non_neutral,
                TreeDetail(tree_in_detail, text_style__non_neutral),
            ),
        ]

        for header_text_style_case in header_text_style_cases:
            with self.subTest(header_text_style_case.name):
                tree_detail = header_text_style_case.actual
                root = Node('the root', False, [tree_detail], ())

                # EXPECTATION #

                expectation = matches_trace_with_details(
                    root,
                    [
                        matches_detail_line_element(tree_in_detail.header,
                                                    depth=0,
                                                    text_style=header_text_style_case.expected),
                    ],
                )

                # ACT & ASSERT #

                _check(self, root, expectation)

    def test_node_with_detail(self):
        # ARRANGE #

        string_detail = StringDetail('the string detail')
        tree_in_detail = Node('the contained tree root', None, (string_detail,), ())

        tree_detail = TreeDetail(tree_in_detail)

        root = Node('the root', False, [tree_detail], ())

        # EXPECTATION #

        expectation = matches_trace_with_details(
            root,
            [
                matches_detail_line_element(tree_in_detail.header, depth=0),
                matches_string_detail_line_element(string_detail, depth=1),
            ],
        )

        # ACT & ASSERT #

        _check(self, root, expectation)

    def test_node_with_child(self):
        # ARRANGE #

        child = Node('the child', None, (), ())
        tree_in_detail = Node('the contained tree root', None, (), (child,))

        text_style__non_neutral = TextStyle(font_style=FontStyle.BOLD)

        header_text_style_cases = [
            NEA(
                'default text style',
                TEXT_STYLE__NEUTRAL,
                TreeDetail(tree_in_detail),
            ),
            NEA(
                'custom text style',
                text_style__non_neutral,
                TreeDetail(tree_in_detail, text_style__non_neutral),
            ),
        ]

        for header_text_style_case in header_text_style_cases:
            with self.subTest(header_text_style_case.name):
                tree_detail = header_text_style_case.actual

                root = Node('the root', False, [tree_detail], ())

                # EXPECTATION #

                expectation = matches_trace_with_details(
                    root,
                    [
                        matches_detail_line_element(tree_in_detail.header,
                                                    depth=0,
                                                    text_style=header_text_style_case.expected),
                        matches_detail_line_element(child.header,
                                                    depth=1,
                                                    text_style=header_text_style_case.expected),
                    ],
                )

                # ACT & ASSERT #

                _check(self, root, expectation)

    def test_node_with_detail_and_child(self):
        # ARRANGE #

        child = Node('the child', None, (), ())
        string_detail = StringDetail('the string detail')
        tree_in_detail = Node('the contained tree root', None, (string_detail,), (child,))

        tree_detail = TreeDetail(tree_in_detail)

        root = Node('the root', False, [tree_detail], ())

        # EXPECTATION #

        expectation = matches_trace_with_details(
            root,
            [
                matches_detail_line_element(tree_in_detail.header, depth=0),
                matches_string_detail_line_element(string_detail, depth=1),
                matches_detail_line_element(child.header, depth=1),
            ],
        )

        # ACT & ASSERT #

        _check(self, root, expectation)

    def test_node_with_child_with_child(self):
        # ARRANGE #

        child_11 = Node('the child 11', None, (), ())
        child_1 = Node('the child 1', None, (), (child_11,))
        tree_in_detail = Node('the contained tree root', None, (), (child_1,))

        tree_detail = TreeDetail(tree_in_detail)

        root = Node('the root', False, [tree_detail], ())

        # EXPECTATION #

        expectation = matches_trace_with_details(
            root,
            [
                matches_detail_line_element(tree_in_detail.header, depth=0),
                matches_detail_line_element(child_1.header, depth=1),
                matches_detail_line_element(child_11.header, depth=2),
            ],
        )

        # ACT & ASSERT #

        _check(self, root, expectation)

    def test_complex(self):
        # ARRANGE #

        child_11_detail = StringDetail('string detail 11')
        child_11 = Node('the child 11', None, (child_11_detail,), ())
        child_1_detail_1 = StringDetail('string detail 1-1')
        child_1_detail_2 = StringDetail('string detail 1-2')
        child_1 = Node('the child 1', None,
                       (child_1_detail_1, child_1_detail_2),
                       (child_11,))
        child_2 = Node('the child 2', None, (), ())
        tree_in_detail = Node('the contained tree root', None, (), (child_1, child_2))

        tree_detail = TreeDetail(tree_in_detail)

        root = Node('the root', False, [tree_detail], ())

        # EXPECTATION #

        expectation = matches_trace_with_details(
            root,
            [
                matches_detail_line_element(tree_in_detail.header, depth=0),
                matches_detail_line_element(child_1.header, depth=1),
                matches_string_detail_line_element(child_1_detail_1, depth=2),
                matches_string_detail_line_element(child_1_detail_2, depth=2),
                matches_detail_line_element(child_11.header, depth=2),
                matches_string_detail_line_element(child_11_detail, depth=3),
                matches_detail_line_element(child_2.header, depth=1),
            ],
        )

        # ACT & ASSERT #

        _check(self, root, expectation)


def _check(put: unittest.TestCase,
           node: Node[bool],
           expectation: Assertion[s.MajorBlock],
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
    Indentation(2, '<MINOR-BLOCK-CUSTOM-INDENT>'),
    '<DETAIL-INDENT>',
)


def matches_trace_with_just_single_detail(trace: Node[bool],
                                          detail: Assertion[s.LineElement],
                                          ) -> Assertion[s.MajorBlock]:
    return matches_trace_with_details(trace, [detail])


def matches_trace_with_details(tree: Node[bool],
                               details: Sequence[Assertion[s.LineElement]],
                               ) -> Assertion[s.MajorBlock]:
    expected_line_elements = asrt.matches_sequence(
        [matches_header_line_element(tree)] +
        list(details)
    )
    return asrt_struct.matches_major_block__w_plain_properties(
        minor_blocks=asrt.matches_singleton_sequence(
            asrt_struct.matches_minor_block(
                line_elements=expected_line_elements,
                properties=matches_node_properties(depth=0),
            ))
    )


def matches_header_line_element(node: Node[bool]) -> Assertion[s.LineElement]:
    return asrt_struct.matches_line_element(
        line_object=asrt_struct.is_string__not_line_ended(asrt.equals(_expected_header_line(node))),
        properties=asrt_struct.equals_element_properties(
            _get_header_style(node)
        ),
    )


def matches_string_detail_line_element(detail: StringDetail, depth: int) -> Assertion[s.LineElement]:
    return asrt_struct.matches_line_element(
        line_object=asrt_struct.is_string__not_line_ended(
            asrt.equals(str(detail.string))),
        properties=matches_detail_properties(depth=depth),
    )


def matches_detail_line_element(string: str,
                                depth: int,
                                text_style: TextStyle = TEXT_STYLE__NEUTRAL) -> Assertion[s.LineElement]:
    return asrt_struct.matches_line_element(
        line_object=asrt_struct.is_string__not_line_ended(
            asrt.equals(string)),
        properties=matches_detail_properties(depth=depth, text_style=text_style),
    )


def matches_pre_formatted_string_detail_line_element(detail: PreFormattedStringDetail,
                                                     depth: int,
                                                     ) -> Assertion[s.LineElement]:
    return asrt_struct.matches_line_element(
        line_object=asrt_struct.is_pre_formatted_string(
            string=asrt.equals(str(detail.object_with_to_string)),
            string_is_line_ended=asrt.equals(detail.string_is_line_ended),
        ),
        properties=matches_detail_properties(depth=depth),
    )


def matches_header_properties(node: Node[bool]) -> Assertion[s.ElementProperties]:
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


def expected_node_indentation(depth: int) -> Indentation:
    return Indentation(depth * RENDERING_CONFIGURATION.minor_block_indent.level,
                       depth * RENDERING_CONFIGURATION.minor_block_indent.suffix)


def expected_node_properties(depth: int) -> s.ElementProperties:
    return s.ElementProperties(
        expected_node_indentation(depth),
        TEXT_STYLE__NEUTRAL,
    )


def matches_node_properties(depth: int) -> Assertion[s.ElementProperties]:
    return asrt_struct.equals_element_properties(expected_node_properties(depth))


def expected_detail_properties(depth: int,
                               text_style: TextStyle = TEXT_STYLE__NEUTRAL) -> s.ElementProperties:
    return s.ElementProperties(
        Indentation(depth + 1,
                    RENDERING_CONFIGURATION.detail_indent),
        text_style,
    )


def matches_detail_properties(depth: int,
                              text_style: TextStyle = TEXT_STYLE__NEUTRAL) -> Assertion[s.ElementProperties]:
    return asrt_struct.equals_element_properties(expected_detail_properties(depth, text_style))


STRING_OBJECT_CASES = [
    NameAndValue('constant',
                 'a string constant',
                 ),
    NameAndValue('must apply str',
                 str_constructor.FormatPositional(
                     '{}',
                     'a string that is generated',
                 ),
                 ),
]

_HEADER_PROPERTIES_FOR_F = ElementProperties(INDENTATION__NEUTRAL,
                                             TextStyle(color=ForegroundColor.RED,
                                                       font_style=FontStyle.BOLD),
                                             )
_HEADER_PROPERTIES_FOR_T = ElementProperties(INDENTATION__NEUTRAL,
                                             TextStyle(color=ForegroundColor.GREEN),
                                             )
