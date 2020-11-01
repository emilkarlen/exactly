import unittest

from exactly_lib.util.description_tree.tree import Node, Detail, DetailVisitor, RET
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_prims.trace.test_resources import trace_rendering_assertions as sut
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions as asrt_d_tree


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestDefaultAssertions),
        unittest.makeSuite(TestAssertionOnRenderedNode),
    ])


class TestDefaultAssertions(unittest.TestCase):
    def test_success_WHEN_actual_is_valid(self):
        assertion = sut.matches_node_renderer()
        assertion.apply_without_message(self,
                                        NodeRendererForTest(Node('header', None, [], [])))

    def test_fail_WHEN_invalid_type(self):
        # ARRANGE #
        assertion = sut.matches_node_renderer()
        cases = [
            NameAndValue('invalid type of node renderer',
                         'not a' + str(sut.NodeRenderer)
                         ),
            NameAndValue('result of rendering is object of invalid type',
                         NodeRendererForTest('not a Node')
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion, case.value)


class TestAssertionOnRenderedNode(unittest.TestCase):
    def test_fail(self):
        actual = sut.Node('actual header', None, [], [])
        expectation = asrt_d_tree.matches_node(header=asrt.equals('expected header'))

        assertion = sut.matches_node_renderer(rendered_node=expectation)

        assert_that_assertion_fails(assertion,
                                    NodeRendererForTest(actual))

    def test_succeed(self):
        actual = sut.Node('expected header', None, [], [])
        expectation = asrt_d_tree.matches_node(header=asrt.equals('expected header'))

        assertion = sut.matches_node_renderer(rendered_node=expectation)

        assertion.apply_without_message(self,
                                        NodeRendererForTest(actual))


class NodeRendererForTest(sut.NodeRenderer):
    def __init__(self, result):
        self.result = result

    def render(self) -> Node:
        return self.result


class DetailForTest(Detail):
    def accept(self, visitor: DetailVisitor[RET]) -> RET:
        raise NotImplementedError('unsupported')
