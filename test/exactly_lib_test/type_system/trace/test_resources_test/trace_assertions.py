import unittest

from exactly_lib.type_system.trace.trace import DetailVisitor, RET
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.trace.test_resources import trace_assertions as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestDefaultAssertions),
        unittest.makeSuite(TestAssertionOnHeader),
        unittest.makeSuite(TestAssertionOnData),
        unittest.makeSuite(TestAssertionOnDetails),
        unittest.makeSuite(TestAssertionOnChildren),
        unittest.makeSuite(TestIsStringDetail),
        unittest.makeSuite(TestIsPreFormattedStringDetail),
        unittest.makeSuite(TestAnyDetail),
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


class TestIsStringDetail(unittest.TestCase):
    def test_matches(self):
        expected_string = 'expected string'
        cases = [
            NEA('default',
                expected=
                sut.is_string_detail(),
                actual=
                sut.StringDetail('anything'),
                ),
            NEA('string',
                expected=
                sut.is_string_detail(string=asrt.equals(expected_string)),
                actual=
                sut.StringDetail(expected_string)
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('unexpected object type',
                expected=
                sut.is_string_detail(),
                actual=
                sut.PreFormattedStringDetail('s'),
                ),
            NEA('string',
                expected=
                sut.is_string_detail(string=asrt.equals('expected')),
                actual=
                sut.StringDetail('actual'),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestIsPreFormattedStringDetail(unittest.TestCase):
    def test_matches(self):
        expected_string = 'expected string'
        cases = [
            NEA('default/False',
                expected=
                sut.is_pre_formatted_string_detail(),
                actual=
                sut.PreFormattedStringDetail('anything', False),
                ),
            NEA('default/True',
                expected=
                sut.is_pre_formatted_string_detail(),
                actual=
                sut.PreFormattedStringDetail('anything', True),
                ),
            NEA('object_with_to_string',
                expected=
                sut.is_pre_formatted_string_detail(object_with_to_string=asrt.equals(expected_string)),
                actual=
                sut.PreFormattedStringDetail(expected_string, True)
                ),
            NEA('string is line ended',
                expected=
                sut.is_pre_formatted_string_detail(string_is_line_ended=asrt.equals(True)),
                actual=
                sut.PreFormattedStringDetail('anything', True),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('unexpected object type',
                expected=
                sut.is_pre_formatted_string_detail(),
                actual=
                sut.StringDetail('s'),
                ),
            NEA('string',
                expected=
                sut.is_pre_formatted_string_detail(object_with_to_string=asrt.equals('expected')),
                actual=
                sut.PreFormattedStringDetail('actual', True),
                ),
            NEA('string is line ended',
                expected=
                sut.is_pre_formatted_string_detail(string_is_line_ended=asrt.equals(True)),
                actual=
                sut.PreFormattedStringDetail('anything', False),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestAnyDetail(unittest.TestCase):
    def test_matches(self):
        cases = [
            sut.StringDetail('s'),
            sut.PreFormattedStringDetail('pre-formatted', True),
        ]
        for line_object in cases:
            with self.subTest(str(type(line_object))):
                sut.is_any_detail().apply_without_message(self, line_object)

    def test_not_matches(self):
        cases = [
            NameAndValue('not a sub class of LineObject',
                         'not a LineObject'
                         ),
            NameAndValue('Unknown sub class of LineObject',
                         DetailForTest()
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(sut.is_any_detail(), case.value)


class DetailForTest(sut.Detail):
    def accept(self, visitor: DetailVisitor[RET]) -> RET:
        raise NotImplementedError('unsupported')
