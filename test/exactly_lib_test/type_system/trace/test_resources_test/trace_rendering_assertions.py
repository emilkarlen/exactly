import pathlib
import unittest

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment
from exactly_lib.type_system.trace.trace import Node, Detail
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_sds
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.trace.test_resources import trace_assertions as asrt_trace
from exactly_lib_test.type_system.trace.test_resources import trace_rendering_assertions as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestDefaultAssertions),
        unittest.makeSuite(TestAssertionOnRenderedNode),
        unittest.makeSuite(TestGivenEnvironmentIsUsed),
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
        expectation = asrt_trace.matches_node(header=asrt.equals('expected header'))

        assertion = sut.matches_node_renderer(rendered_node=expectation)

        assert_that_assertion_fails(assertion,
                                    NodeRendererForTest(actual))

    def test_succeed(self):
        actual = sut.Node('expected header', None, [], [])
        expectation = asrt_trace.matches_node(header=asrt.equals('expected header'))

        assertion = sut.matches_node_renderer(rendered_node=expectation)

        assertion.apply_without_message(self,
                                        NodeRendererForTest(actual))


class TestGivenEnvironmentIsUsed(unittest.TestCase):
    def test(self):
        renderer = NodeRendererThatUsesHomeCaseDirAsHeader()
        given_environment = ErrorMessageResolvingEnvironment(
            HomeAndSds(
                HomeDirectoryStructure(pathlib.Path('home-case'),
                                       pathlib.Path('home-act')),
                fake_sds(),
            )
        )
        assertion = sut.matches_node_renderer(
            rendered_node=asrt_trace.matches_node(header=asrt.equals(str(given_environment.tcds.hds.case_dir))),
            in_environment=given_environment,
        )

        # ACT & ASSERT #

        assertion.apply_without_message(self, renderer)


class NodeRendererForTest(sut.NodeRenderer):
    def __init__(self, result):
        self.result = result

    def render(self, environment: ErrorMessageResolvingEnvironment) -> Node:
        return self.result


class NodeRendererThatUsesHomeCaseDirAsHeader(sut.NodeRenderer):
    def render(self, environment: ErrorMessageResolvingEnvironment) -> Node:
        return sut.Node(str(environment.tcds.hds.case_dir), None, [], [])


class DetailForTest(Detail):
    pass
