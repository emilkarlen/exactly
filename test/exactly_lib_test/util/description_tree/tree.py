import unittest

from exactly_lib.util import strings
from exactly_lib.util.description_tree import tree as sut
from exactly_lib.util.description_tree.tree import PreFormattedStringDetail, HeaderAndValueDetail, StringDetail
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestNode),
        unittest.makeSuite(TestStringDetail),
        unittest.makeSuite(TestPreFormattedStringDetail),
        unittest.makeSuite(TestHeaderAndValueDetail),
    ])


class TestNode(unittest.TestCase):
    def test(self):
        # ARRANGE #
        detail = sut.StringDetail('a detail')
        child = sut.Node('child header', False, (), ())
        root_header = 'root header'
        root_data = True
        root = sut.Node(root_header, root_data, (detail,), (child,))

        # ACT & ASSERT #

        self.assertEqual(root_header,
                         root.header,
                         'root header')

        self.assertEqual(root_data,
                         root.data,
                         'root data')

        expected_root_details = asrt.matches_singleton_sequence(
            asrt.is_(detail)
        )

        expected_root_details.apply_with_message(self,
                                                 root.details,
                                                 'root details')

        expected_root_children = asrt.matches_singleton_sequence(
            asrt.is_(child)
        )

        expected_root_children.apply_with_message(self,
                                                  root.children,
                                                  'root children')


class TestStringDetail(unittest.TestCase):
    def test_attributes(self):
        # ARRANGE #
        cases = [
            NameAndValue(
                'plain string',
                'the plain string'
            ),
            NameAndValue(
                'to-string object',
                strings.FormatPositional('template {}', 'value')
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT && ASSERT #
                detail = sut.StringDetail(case.value)
                self.assertIs(case.value,
                              detail.string)

    def test_accept_visitor(self):
        # ARRANGE #

        visitor = _VisitorThatRegistersVisitedClassesAndReturnsConstant(72)

        detail = sut.StringDetail('the string')

        # ACT #

        ret_val_from_visitor = detail.accept(visitor)

        # ASSERT #
        self.assertEqual(visitor.ret_val,
                         ret_val_from_visitor,
                         'return value')

        self.assertEqual(visitor.visited_classes,
                         [sut.StringDetail],
                         'visited classes')


class TestPreFormattedStringDetail(unittest.TestCase):
    def test_attributes(self):
        # ARRANGE #
        cases = [
            NameAndValue(
                'plain string',
                'the plain string'
            ),
            NameAndValue(
                'to-string object',
                strings.FormatPositional('template {}', 'value')
            ),
        ]
        for string_is_line_ended in [False, True]:
            for case in cases:
                with self.subTest(string_is_line_ended=string_is_line_ended,
                                  string=case.name):
                    detail = sut.PreFormattedStringDetail(case.value, string_is_line_ended)

                    # ACT & ASSERT #

                    self.assertIs(case.value,
                                  detail.object_with_to_string,
                                  'object_with_to_string')

                    self.assertIs(string_is_line_ended,
                                  detail.string_is_line_ended,
                                  'string_is_line_ended')

    def test_accept_visitor(self):
        # ARRANGE #

        visitor = _VisitorThatRegistersVisitedClassesAndReturnsConstant(69)

        detail = sut.PreFormattedStringDetail('the string', False)

        # ACT #

        ret_val_from_visitor = detail.accept(visitor)

        # ASSERT #
        self.assertEqual(visitor.ret_val,
                         ret_val_from_visitor,
                         'return value')

        self.assertEqual(visitor.visited_classes,
                         [sut.PreFormattedStringDetail],
                         'visited classes')


class TestHeaderAndValueDetail(unittest.TestCase):
    def test_attributes(self):
        # ARRANGE #
        header = 'the header'
        value = sut.StringDetail('the value detail header')
        detail = sut.HeaderAndValueDetail(header, [value])

        # ACT & ASSERT #

        self.assertIs(header,
                      detail.header,
                      'header')

        expected_values = asrt.matches_singleton_sequence(asrt.is_(value))

        expected_values.apply_with_message(self,
                                           detail.values,
                                           'values')

    def test_accept_visitor(self):
        # ARRANGE #

        visitor = _VisitorThatRegistersVisitedClassesAndReturnsConstant(69)

        detail = sut.HeaderAndValueDetail('the header', [])

        # ACT #

        ret_val_from_visitor = detail.accept(visitor)

        # ASSERT #
        self.assertEqual(visitor.ret_val,
                         ret_val_from_visitor,
                         'return value')

        self.assertEqual(visitor.visited_classes,
                         [sut.HeaderAndValueDetail],
                         'visited classes')


class _VisitorThatRegistersVisitedClassesAndReturnsConstant(sut.DetailVisitor[int]):
    def __init__(self, ret_val: int):
        self.visited_classes = []
        self.ret_val = ret_val

    def visit_string(self, x: StringDetail) -> int:
        self.visited_classes.append(StringDetail)
        return self.ret_val

    def visit_pre_formatted_string(self, x: PreFormattedStringDetail) -> int:
        self.visited_classes.append(PreFormattedStringDetail)
        return self.ret_val

    def visit_header_and_value(self, x: HeaderAndValueDetail) -> int:
        self.visited_classes.append(HeaderAndValueDetail)
        return self.ret_val
