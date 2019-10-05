import unittest

from exactly_lib.util.description_tree import renderers as sut
from exactly_lib.util.description_tree.renderer import NodeRenderer, NODE_DATA
from exactly_lib.util.description_tree.tree import Node
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions as asrt_d_tree


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestCachedSingleInvokation)


class TestCachedSingleInvokation(unittest.TestCase):
    def test_gives_the_constant_on_first_invokation(self):
        # ARRANGE #

        node = Node('header', None, (), ())
        renderer = sut.CachedSingleInvokation(
            _ConstRendererThatRaisesExceptionOn2ndInvokation(node)
        )

        # ACT #

        actual = renderer.render()

        # ASSERT #

        expectation = _equals_empty_node(node)

        expectation.apply_without_message(self, actual)

    def test_does_single_invokation(self):
        # ARRANGE #

        node = Node('header', None, (), ())
        renderer = sut.CachedSingleInvokation(
            _ConstRendererThatRaisesExceptionOn2ndInvokation(node)
        )

        # ACT #

        actual_1 = renderer.render()
        actual_2 = renderer.render()

        # ASSERT #

        expectation = _equals_empty_node(node)

        expectation.apply_with_message(self, actual_1, '1st invokation')
        expectation.apply_with_message(self, actual_2, '2nd invokation')


class _ConstRendererThatRaisesExceptionOn2ndInvokation(NodeRenderer[NODE_DATA]):
    def __init__(self, constant: Node[NODE_DATA]):
        self._constant = constant
        self._invokation_has_been_done = False

    def render(self) -> Node[NODE_DATA]:
        if self._invokation_has_been_done:
            raise ValueError('invokation has already been done')

        self._invokation_has_been_done = True
        return self._constant


def _equals_empty_node(expected: Node) -> ValueAssertion[Node]:
    return asrt_d_tree.matches_node(
        header=asrt.equals(expected.header),
        data=asrt.equals(expected.data),
        details=asrt.is_empty_sequence,
        children=asrt.is_empty_sequence,
    )
