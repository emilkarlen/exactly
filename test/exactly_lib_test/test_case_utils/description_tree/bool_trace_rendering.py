import unittest

from exactly_lib.test_case_utils.description_tree import bool_trace_rendering as sut
from exactly_lib.type_system.trace.trace_renderer import NodeRenderer
from exactly_lib.util.ansi_terminal_color import ForegroundColor
from exactly_lib.util.description_tree.tree import Node, StringDetail
from exactly_lib.util.simple_textstruct import structure as s
from exactly_lib.util.simple_textstruct.structure import ElementProperties, INDENTATION__NEUTRAL, TextStyle, \
    Indentation, TEXT_STYLE__NEUTRAL
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.simple_textstruct.test_resources import structure_assertions as asrt_struct


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_header(self):
        # ARRANGE #
        for data in [False, True]:
            with self.subTest(data=data):
                root = Node('header', data, (), ())
                renderer = _ConstantNodeRenderer(root)

                # EXPECTATION #

                expectation = asrt_struct.matches_major_block__w_plain_properties(
                    minor_blocks=asrt.matches_singleton_sequence(
                        asrt_struct.matches_minor_block__w_plain_properties(
                            line_elements=asrt.matches_singleton_sequence(
                                _matches_header_line_element(root)
                            ),
                        )
                    )
                )

                # ACT & ASSERT #

                _check(self, root, expectation)

    def test_detail(self):
        # ARRANGE #

        for child_data in [False, True]:
            with self.subTest(data=child_data):
                detail = StringDetail('the detail')
                root = Node('the root', False, [detail], [])

                # EXPECTATION #

                expectation = asrt_struct.matches_major_block__w_plain_properties(
                    minor_blocks=asrt.matches_singleton_sequence(asrt_struct.matches_minor_block__w_plain_properties(
                        line_elements=asrt.matches_sequence([
                            _matches_header_line_element(root),
                            _matches_string_detail_line_element(detail, depth=0),
                        ]),
                    ))
                )

                # ACT & ASSERT #

                _check(self, root, expectation)


def _check(put: unittest.TestCase,
           rendered_node: Node[bool],
           expectation: ValueAssertion[s.MajorBlock],
           ):
    renderer = sut.BoolTraceRenderer(_ConstantNodeRenderer(rendered_node))

    # ACT #

    actual = renderer.render()

    # ASSERT #

    expectation.apply_without_message(put, actual)


def _matches_header_line_element(node: Node[bool]) -> ValueAssertion[s.LineElement]:
    return asrt_struct.matches_line_element(
        line_object=asrt_struct.is_string__not_line_ended(
            asrt.equals(_expected_header_str(node))
        ),
        properties=asrt_struct.equals_element_properties(
            _expected_header_style(node)
        ),
    )


def _expected_header_style(node: Node[bool]) -> ElementProperties:
    return ElementProperties(INDENTATION__NEUTRAL,
                             TextStyle(color=_expected_header_color(node)),
                             )


def _matches_string_detail_line_element(detail: StringDetail, depth: int) -> ValueAssertion[s.LineElement]:
    return asrt_struct.matches_line_element(
        line_object=asrt_struct.is_string__not_line_ended(
            asrt.equals(str(detail.string))),
        properties=asrt_struct.equals_element_properties(
            expected_detail_properties(level=depth + 1)
        ),
    )


def _expected_header_str(node: Node[bool]) -> str:
    bool_flag = (
        'T'
        if node.data
        else
        'F'
    )
    return ''.join(['(', bool_flag, ')', ' ', node.header])


def _expected_header_color(node: Node[bool]) -> ForegroundColor:
    return (
        ForegroundColor.BRIGHT_GREEN
        if node.data
        else
        ForegroundColor.BRIGHT_RED
    )


def expected_detail_properties(level: int) -> s.ElementProperties:
    return s.ElementProperties(
        Indentation(level,
                    _EXPECTED_DETAIL_INDENT_SUFFIX),
        TEXT_STYLE__NEUTRAL,
    )


class _ConstantNodeRenderer(NodeRenderer[bool]):
    def __init__(self, constant: Node[bool]):
        self._constant = constant

    def render(self) -> Node[bool]:
        return self._constant


_EXPECTED_DETAIL_INDENT_SUFFIX = ' ' * len('(B) ')
