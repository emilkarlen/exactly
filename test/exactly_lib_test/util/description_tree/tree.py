import unittest

from exactly_lib.util import strings
from exactly_lib.util.description_tree import tree as sut
from exactly_lib.util.description_tree.tree import PreFormattedStringDetail, HeaderAndValueDetail, StringDetail, \
    TreeDetail, IndentedDetail
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestNode),
        unittest.makeSuite(TestStringDetail),
        unittest.makeSuite(TestPreFormattedStringDetail),
        unittest.makeSuite(TestHeaderAndValueDetail),
        unittest.makeSuite(TestIndented),
        unittest.makeSuite(TestTreeDetail),
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

        visitor = _VisitorThatRegistersVisitedClassesAndReturnsConstant()

        detail = sut.StringDetail('the string')

        # ACT #

        detail.accept(visitor)

        # ASSERT #

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

        visitor = _VisitorThatRegistersVisitedClassesAndReturnsConstant()

        detail = sut.PreFormattedStringDetail('the string', False)

        # ACT #

        detail.accept(visitor)

        # ASSERT #

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

        visitor = _VisitorThatRegistersVisitedClassesAndReturnsConstant()

        detail = sut.HeaderAndValueDetail('the header', [])

        # ACT #

        detail.accept(visitor)

        # ASSERT #

        self.assertEqual(visitor.visited_classes,
                         [sut.HeaderAndValueDetail],
                         'visited classes')


class TestIndented(unittest.TestCase):
    def test_attributes(self):
        # ARRANGE #
        a_detail = sut.StringDetail('the string')
        indented = [a_detail]
        detail = sut.IndentedDetail(indented)

        # ACT & ASSERT #

        self.assertIs(indented,
                      detail.details,
                      'details')

        expected_values = asrt.matches_singleton_sequence(asrt.is_(a_detail))

        expected_values.apply_with_message(self,
                                           detail.details,
                                           'details')

    def test_accept_visitor(self):
        # ARRANGE #

        visitor = _VisitorThatRegistersVisitedClassesAndReturnsConstant()

        detail = sut.IndentedDetail([sut.StringDetail('the string')])

        # ACT #

        detail.accept(visitor)

        # ASSERT #

        self.assertEqual(visitor.visited_classes,
                         [sut.IndentedDetail],
                         'visited classes')


class TestTreeDetail(unittest.TestCase):
    def test_attributes(self):
        # ARRANGE #

        tree = sut.Node('header', 'data', (), ())
        detail = sut.TreeDetail(tree)

        # ACT & ASSERT #

        self.assertIs(tree,
                      detail.tree)

    def test_accept_visitor(self):
        # ARRANGE #

        visitor = _VisitorThatRegistersVisitedClassesAndReturnsConstant()

        node = sut.Node('header', 'data', (), ())
        detail = sut.TreeDetail(node)

        # ACT #

        detail.accept(visitor)

        # ASSERT #
        self.assertEqual(visitor.visited_classes,
                         [sut.TreeDetail],
                         'visited classes')


class _VisitorThatRegistersVisitedClassesAndReturnsConstant(sut.DetailVisitor[None]):
    def __init__(self):
        self.visited_classes = []

    def visit_string(self, x: StringDetail) -> None:
        self.visited_classes.append(StringDetail)

    def visit_pre_formatted_string(self, x: PreFormattedStringDetail) -> None:
        self.visited_classes.append(PreFormattedStringDetail)

    def visit_header_and_value(self, x: HeaderAndValueDetail) -> None:
        self.visited_classes.append(HeaderAndValueDetail)

    def visit_indented(self, x: IndentedDetail) -> None:
        self.visited_classes.append(IndentedDetail)

    def visit_tree(self, x: TreeDetail) -> None:
        self.visited_classes.append(TreeDetail)
