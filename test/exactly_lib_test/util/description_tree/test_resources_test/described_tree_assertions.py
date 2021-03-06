import copy
import unittest
from typing import Sequence

from exactly_lib.util.description_tree.tree import StringDetail, DetailVisitor, RET
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions as sut
from exactly_lib_test.util.test_resources import to_string_assertions as asrt_to_string


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestDefaultAssertions),
        unittest.makeSuite(TestAssertionOnHeader),
        unittest.makeSuite(TestAssertionOnData),
        unittest.makeSuite(TestAssertionOnDetails),
        unittest.makeSuite(TestAssertionOnChildren),
        unittest.makeSuite(TestIsStringDetail),
        unittest.makeSuite(TestIsPreFormattedStringDetail),
        unittest.makeSuite(TestIsHeaderAndValueDetail),
        unittest.makeSuite(TestIsIndentedDetail),
        unittest.makeSuite(TestIsTreeDetail),
        unittest.makeSuite(TestIsAnyDetail),
        unittest.makeSuite(TestHeaderDataAndChildrenEquals),
        unittest.makeSuite(TestEqualsDetail),
        unittest.makeSuite(TestEqualsNode),
    ])


class TestHeaderDataAndChildrenEquals(unittest.TestCase):
    def test_matches(self):
        # ARRANGE #
        cases = [
            NameAndValue(
                'empty',
                sut.Node('the header', 'the data', (), ()),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assertion = sut.header_data_and_children_equal_as(case.value)
                # ACT & ASSERT #
                assertion.apply_without_message(self, case.value)

    def test_not_matches(self):
        # ARRANGE #
        cases = [
            NEA(
                'different header',
                expected=sut.Node('the expected header', None, (), ()),
                actual=sut.Node('the actual header', None, (), ()),
            ),
            NEA(
                'different data',
                expected=sut.Node('', 'expected', (), ()),
                actual=sut.Node('', 'actual', (), ()),
            ),
            NEA(
                'different number of children',
                expected=sut.Node('', None, (), (sut.Node('child', None, (), ()),)),
                actual=sut.Node('', None, (), ()),
            ),
            NEA(
                'different child',
                expected=
                sut.Node('', None, (), (sut.Node('expected child', None, (), ()),)),
                actual=
                sut.Node('', None, (), (sut.Node('actual child', None, (), ()),)),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assertion = sut.header_data_and_children_equal_as(case.expected)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion, case.actual)


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
                                  [StringDetail('the string')],
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
                sut.is_string_detail(to_string_object=asrt_to_string.equals(expected_string)),
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
                sut.is_string_detail(to_string_object=asrt_to_string.equals('expected')),
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
                sut.is_pre_formatted_string_detail(to_string_object=asrt_to_string.equals(expected_string)),
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
                sut.is_pre_formatted_string_detail(to_string_object=asrt_to_string.equals('expected')),
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


class TestIsHeaderAndValueDetail(unittest.TestCase):
    def test_matches(self):
        header = 'the header'
        value = StringDetail('the string detail')
        cases = [
            NEA('header',
                expected=
                sut.is_header_and_value_detail(header=asrt.equals(header)),
                actual=
                sut.HeaderAndValueDetail(header, ()),
                ),
            NEA('values',
                expected=
                sut.is_header_and_value_detail(
                    values=asrt.matches_singleton_sequence(asrt.is_(value))
                ),
                actual=
                sut.HeaderAndValueDetail(header, (value,))
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('unexpected object type',
                expected=
                sut.is_header_and_value_detail(),
                actual=
                sut.PreFormattedStringDetail('s'),
                ),
            NEA('header',
                expected=
                sut.is_header_and_value_detail(header=asrt.equals('expected header')),
                actual=
                sut.HeaderAndValueDetail('actual header', ()),
                ),
            NEA('values',
                expected=
                sut.is_header_and_value_detail(values=asrt.is_empty_sequence),
                actual=
                sut.HeaderAndValueDetail('header', (StringDetail('a value'),)),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestIsIndentedDetail(unittest.TestCase):
    def test_matches(self):
        # ARRANGE #
        expected_detail = StringDetail('the string detail')
        actual = sut.IndentedDetail([expected_detail])
        # EXPECTATION #
        assertion = sut.is_indented_detail(
            details=asrt.matches_singleton_sequence(asrt.is_(expected_detail))
        )
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_not_matches(self):
        cases = [
            NEA('unexpected object type',
                expected=
                sut.is_indented_detail(),
                actual=
                sut.PreFormattedStringDetail('s'),
                ),
            NEA('details',
                expected=
                sut.is_indented_detail(details=asrt.is_empty_sequence),
                actual=
                sut.IndentedDetail((StringDetail('a value'),)),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestIsTreeDetail(unittest.TestCase):
    def test_matches(self):
        # ARRANGE #

        node = sut.Node('node header', None, (), ())
        tree_detail = sut.TreeDetail(node)

        satisfied_assertion = asrt.sub_component('header',
                                                 lambda tree: tree.header,
                                                 asrt.equals(node.header))
        # ACT #

        sut.is_tree_detail(satisfied_assertion).apply_without_message(self, tree_detail)

    def test_not_matches(self):
        # ARRANGE #

        node = sut.Node('actual header', None, (), ())
        tree_detail = sut.TreeDetail(node)

        unsatisfied_assertion = asrt.sub_component('header',
                                                   lambda tree: tree.header,
                                                   asrt.equals(node.header + ' with extra'))

        # ACT #

        assert_that_assertion_fails(sut.is_tree_detail(unsatisfied_assertion), tree_detail)


class TestIsAnyDetail(unittest.TestCase):
    def test_matches(self):
        cases = [
            sut.StringDetail('s'),
            sut.PreFormattedStringDetail('pre-formatted', True),
            sut.HeaderAndValueDetail('header', ()),
            sut.TreeDetail(sut.Node('header', None, (), ())),
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


class _EqDetailCase:
    def __init__(self,
                 expected: sut.Detail,
                 unexpected: Sequence[NameAndValue[sut.Detail]],
                 ):
        self.expected = expected
        self.unexpected = unexpected


class _EqNodeCase:
    def __init__(self,
                 name: str,
                 expected: sut.Node,
                 unexpected: Sequence[NameAndValue[sut.Node]],
                 ):
        self.name = name
        self.expected = expected
        self.unexpected = unexpected


HEADER_e = 'expected header'
HEADER_ue = 'unexpected header'
DATA_e = 'expected data'
DATA_ue = 'unexpected data'
S_e = 'expected'
S_ue = 'unexpected'
STRING_DETAIL_e = sut.StringDetail(S_e)
STRING_DETAIL_ue = sut.StringDetail(S_ue)


class TestEqualsDetail(unittest.TestCase):
    DETAILS = [
        _EqDetailCase(
            sut.StringDetail(S_e),
            [
                NameAndValue('unexpected type',
                             sut.PreFormattedStringDetail(S_e)
                             ),
                NameAndValue('unexpected value',
                             sut.StringDetail(S_ue)
                             ),
            ]
        ),
        _EqDetailCase(
            sut.PreFormattedStringDetail(S_e),
            [
                NameAndValue('unexpected type',
                             sut.StringDetail(S_e)
                             ),
                NameAndValue('unexpected value',
                             sut.PreFormattedStringDetail('unexpected')
                             ),
            ]
        ),
        _EqDetailCase(
            sut.HeaderAndValueDetail(HEADER_e, ()),
            [
                NameAndValue('unexpected type',
                             sut.StringDetail(HEADER_e)
                             ),
                NameAndValue('unexpected header',
                             sut.HeaderAndValueDetail(HEADER_ue, ())
                             ),
                NameAndValue('unexpected details',
                             sut.HeaderAndValueDetail(HEADER_e, [sut.StringDetail(S_e)])
                             ),
            ]
        ),
        _EqDetailCase(
            sut.IndentedDetail([sut.StringDetail(S_e)]),
            [
                NameAndValue('unexpected type',
                             sut.StringDetail(HEADER_e)
                             ),
                NameAndValue('unexpected number of children',
                             sut.IndentedDetail([])
                             ),
                NameAndValue('unexpected child',
                             sut.IndentedDetail([sut.StringDetail(S_ue)])
                             ),
            ]
        ),
        _EqDetailCase(
            sut.TreeDetail(sut.Node(HEADER_e, None, [STRING_DETAIL_e], [])),
            [
                NameAndValue('unexpected type',
                             sut.StringDetail(HEADER_e)
                             ),
                NameAndValue('unexpected header',
                             sut.TreeDetail(sut.Node(HEADER_ue, None, [STRING_DETAIL_e], []))
                             ),
                NameAndValue('unexpected number of details',
                             sut.TreeDetail(sut.Node(HEADER_e, None, [], []))
                             ),
                NameAndValue('unexpected child detail',
                             sut.TreeDetail(sut.Node(HEADER_e, None, [STRING_DETAIL_ue], []))
                             ),
            ]
        ),
    ]

    def test_not_equals(self):
        for case in self.DETAILS:
            assertion = sut.equals_detail(case.expected)
            for unexpected in case.unexpected:
                with self.subTest(type=type(case.expected),
                                  unexpected=unexpected.name):
                    assert_that_assertion_fails(assertion, unexpected.value)

    def test_equals(self):
        # ARRANGE #
        for case in self.DETAILS:
            with self.subTest(type=type(case.expected)):
                assertion = sut.equals_detail(case.expected)
                other = copy.deepcopy(case.expected)
                # ACT & ASSERT #
                assertion.apply_without_message(self, other)


class TestEqualsNode(unittest.TestCase):
    def test_equals(self):
        cases = [
            NameAndValue('empty tree',
                         sut.Node.empty(HEADER_e, None)
                         ),
            NameAndValue('tree with data',
                         sut.Node.empty(HEADER_e, 'some data')
                         ),
            NameAndValue('tree with details',
                         sut.Node.leaf(HEADER_e, None, [STRING_DETAIL_e])
                         ),
            NameAndValue('tree with children',
                         sut.Node(HEADER_e, 'root data', [], [sut.Node.empty(HEADER_e, 'child data')])
                         ),
            NameAndValue('tree with details and children',
                         sut.Node(HEADER_e, 'root data',
                                  [STRING_DETAIL_e],
                                  [sut.Node.empty(HEADER_e, 'child data')])
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assertion = sut.equals_node(case.value)
                actual = copy.deepcopy(case.value)
                assertion.apply_without_message(self, actual)

    def test_not_equals(self):
        child_e = sut.Node.empty(HEADER_e, DATA_e)
        child_ue = sut.Node.empty(HEADER_ue, DATA_e)
        cases = [
            _EqNodeCase(
                'empty tree',
                sut.Node.empty(HEADER_e, DATA_e),
                [
                    NameAndValue('unexpected header',
                                 sut.Node.empty(HEADER_ue, DATA_e)
                                 ),
                    NameAndValue('unexpected data',
                                 sut.Node.empty(HEADER_e, DATA_ue)
                                 ),
                ]
            ),
            _EqNodeCase(
                'tree with detail',
                sut.Node.leaf(HEADER_e, DATA_e, [STRING_DETAIL_e]),
                [
                    NameAndValue('no details',
                                 sut.Node.empty(HEADER_e, DATA_e)
                                 ),
                    NameAndValue('too many no details',
                                 sut.Node.leaf(HEADER_e, DATA_e, [STRING_DETAIL_e, STRING_DETAIL_e])
                                 ),
                    NameAndValue('unequal detail',
                                 sut.Node.leaf(HEADER_e, DATA_e, [STRING_DETAIL_ue])
                                 ),
                ]
            ),
            _EqNodeCase(
                'tree with multiple details',
                sut.Node.leaf(HEADER_e, DATA_e,
                              [STRING_DETAIL_e, STRING_DETAIL_e]),
                [
                    NameAndValue('unequal detail',
                                 sut.Node.leaf(HEADER_e, DATA_e,
                                               [STRING_DETAIL_e, STRING_DETAIL_ue])
                                 ),
                ]
            ),
            _EqNodeCase(
                'tree with child',
                sut.Node(HEADER_e, DATA_e, [], [child_e]),
                [
                    NameAndValue('no children',
                                 sut.Node.empty(HEADER_e, DATA_e)
                                 ),
                    NameAndValue('too many no children',
                                 sut.Node(HEADER_e, DATA_e, [], [child_e, child_e])
                                 ),
                    NameAndValue('unequal child',
                                 sut.Node(HEADER_e, DATA_e, [], [child_ue])
                                 ),
                ]
            ),
            _EqNodeCase(
                'tree with multiple children',
                sut.Node(HEADER_e, DATA_e, (),
                         [child_e, child_e]),
                [
                    NameAndValue('unequal child',
                                 sut.Node(HEADER_e, DATA_e, (),
                                          [child_e, child_ue])
                                 ),
                ]
            ),
            _EqNodeCase(
                'tree with details and children',
                sut.Node(HEADER_e, DATA_e, [STRING_DETAIL_e], [child_e]),
                [
                    NameAndValue('unequal detail',
                                 sut.Node(HEADER_e, DATA_e, [STRING_DETAIL_ue], [child_e])
                                 ),
                    NameAndValue('unequal child',
                                 sut.Node(HEADER_e, DATA_e, [STRING_DETAIL_e], [child_ue])
                                 ),
                ]
            ),
        ]
        for case in cases:
            assertion = sut.equals_node(case.expected)
            for unexpected in case.unexpected:
                with self.subTest(expected=case.name,
                                  unexpected=unexpected.name):
                    # ACT & ASSERT #
                    assert_that_assertion_fails(assertion, unexpected.value)


class DetailForTest(sut.Detail):
    def accept(self, visitor: DetailVisitor[RET]) -> RET:
        raise NotImplementedError('unsupported')
