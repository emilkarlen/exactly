import unittest

from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as sut
from exactly_lib_test.type_val_prims.trace.test_resources import trace_rendering_assertions as asrt_trace_rendering
from exactly_lib_test.type_val_prims.trace.test_resources_test.trace_rendering_assertions import NodeRendererForTest
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions as asrt_d_tree


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestDefaultAssertions),
        unittest.makeSuite(TestAssertionOnRenderer),
        unittest.makeSuite(TestAssertionOnValue),
    ])


class TestDefaultAssertions(unittest.TestCase):
    def test_success_WHEN_actual_is_valid(self):
        assertion = sut.matches()
        for result_case in False, True:
            renderer = NodeRendererForTest(Node('header', result_case, [], []))
            actual = MatchingResult(result_case, renderer)
            with self.subTest(case=result_case):
                assertion.apply_without_message(self, actual)

    def test_fail_WHEN_invalid_type(self):
        # ARRANGE #
        assertion = sut.matches()
        cases = [
            NameAndValue('invalid type of object',
                         'not a' + str(MatchingResult)
                         ),
            NameAndValue('invalid type of result',
                         MatchingResult('not a bool', NodeRendererForTest(_ARBITRARY_VALID_NODE))
                         ),
            NameAndValue('invalid type of renderer',
                         MatchingResult(False, 'not a ' + str(sut.NodeRenderer))
                         ),
            NameAndValue('result of rendering is object of invalid type',
                         NodeRendererForTest('not a Node')
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion, case.value)


class TestAssertionOnRenderer(unittest.TestCase):
    def test_fail(self):
        actual_rendered_node = Node('actual header', False, [], [])
        actual_result = MatchingResult(actual_rendered_node.data,
                                       NodeRendererForTest(actual_rendered_node))

        renderer_assertion = asrt_trace_rendering.matches_node_renderer(
            rendered_node=asrt_d_tree.matches_node(header=asrt.equals('expected header'))
        )

        assertion = sut.matches(trace=renderer_assertion)

        assert_that_assertion_fails(assertion,
                                    actual_result)

    def test_succeed(self):
        actual_rendered_node = _trace_for(False)
        actual_result = MatchingResult(actual_rendered_node.data,
                                       NodeRendererForTest(actual_rendered_node))

        renderer_assertion = asrt_trace_rendering.matches_node_renderer(
            rendered_node=asrt_d_tree.matches_node(header=asrt.equals(actual_rendered_node.header))
        )

        assertion = sut.matches(trace=renderer_assertion)

        assertion.apply_without_message(self, actual_result)


class TestAssertionOnValue(unittest.TestCase):

    def test_fail(self):
        actual_value = False
        trace = NodeRendererForTest(_trace_for(actual_value))

        actual_result = MatchingResult(actual_value,
                                       trace)

        assertion = sut.matches(value=asrt.equals(not actual_value))

        assert_that_assertion_fails(assertion,
                                    actual_result)

    def test_succeed(self):
        actual_value = False
        trace = NodeRendererForTest(_trace_for(actual_value))

        actual_result = MatchingResult(actual_value,
                                       trace)

        assertion = sut.matches(value=asrt.equals(actual_value))

        assertion.apply_without_message(self, actual_result)


def _trace_for(value: bool) -> Node[bool]:
    return Node('header', value, [], [])


_ARBITRARY_VALID_NODE = _trace_for(False)
