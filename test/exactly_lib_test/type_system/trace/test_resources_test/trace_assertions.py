import unittest

from exactly_lib.type_system.trace.trace import DetailVisitor, RET
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.trace.test_resources import trace_assertions as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestDefaultAssertions),
        unittest.makeSuite(TestAssertionOnHeader),
        unittest.makeSuite(TestAssertionOnData),
        unittest.makeSuite(TestAssertionOnDetails),
        unittest.makeSuite(TestAssertionOnChildren),
    ])


class TestDefaultAssertions(unittest.TestCase):
    def test_success_WHEN_actual_is_valid_node(self):
        # ARRANGE #
        assertion = sut.matches_node()
        cases = [
            NameAndValue('no details and no children',
                         sut.Node('header',
                                  None,
                                  [],
                                  [])
                         ),
            NameAndValue('single valid detail',
                         sut.Node('header',
                                  None,
                                  [DetailForTest()],
                                  [])
                         ),
            NameAndValue('single valid child',
                         sut.Node('header',
                                  None,
                                  [],
                                  [sut.Node('child node', None, [], [])])
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                assertion.apply_without_message(self, case.value)

    def test_fail_WHEN_invalid_components_of_invalid_type(self):
        # ARRANGE #
        assertion = sut.matches_node()
        cases = [
            NameAndValue('invalid type of header',
                         sut.Node(None,
                                  None,
                                  [],
                                  [])
                         ),
            NameAndValue('invalid type of detail',
                         sut.Node('header',
                                  None,
                                  ['not a Detail'],
                                  [])
                         ),
            NameAndValue('invalid type of child',
                         sut.Node('header',
                                  None,
                                  [],
                                  ['not a Node'])
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion, case.value)


class TestAssertionOnHeader(unittest.TestCase):
    def test_fail(self):
        assertion = sut.matches_node(header=asrt.equals('expected header'))

        assert_that_assertion_fails(assertion,
                                    sut.Node('actual header', None, [], []))

    def test_succeed(self):
        assertion = sut.matches_node(header=asrt.equals('expected header'))

        assertion.apply_without_message(self,
                                        sut.Node('expected header', None, [], []))


class TestAssertionOnData(unittest.TestCase):
    def test_fail(self):
        assertion = sut.matches_node(data=asrt.equals('expected data'))

        assert_that_assertion_fails(assertion,
                                    sut.Node('header', 'actual data', [], []))

    def test_succeed(self):
        assertion = sut.matches_node(data=asrt.equals('expected data'))

        assertion.apply_without_message(self,
                                        sut.Node('header', 'expected data', [], []))


class TestAssertionOnDetails(unittest.TestCase):
    def test_fail(self):
        assertion = sut.matches_node(details=asrt.len_equals(1))

        assert_that_assertion_fails(assertion,
                                    sut.Node('header', None, [], []))

    def test_succeed(self):
        assertion = sut.matches_node(details=asrt.len_equals(0))

        assertion.apply_without_message(self,
                                        sut.Node('header', None, [], []))


class TestAssertionOnChildren(unittest.TestCase):
    def test_fail(self):
        assertion = sut.matches_node(children=asrt.len_equals(1))

        assert_that_assertion_fails(assertion,
                                    sut.Node('header', None, [], []))

    def test_succeed(self):
        assertion = sut.matches_node(children=asrt.len_equals(0))

        assertion.apply_without_message(self,
                                        sut.Node('header', None, [], []))


class DetailForTest(sut.Detail):
    def accept(self, visitor: DetailVisitor[RET]) -> RET:
        raise NotImplementedError('unsupported')
