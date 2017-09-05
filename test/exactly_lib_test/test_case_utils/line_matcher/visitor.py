import unittest

from exactly_lib.test_case_utils.line_matcher import line_matchers as sut
from exactly_lib.util.dir_contents_selection import Selectors


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestLineMatcherStructureVisitor),
    ])


class TestLineMatcherStructureVisitor(unittest.TestCase):
    def test_visit_regex(self):
        # ARRANGE #
        instance = sut.LineMatcherRegex(Selectors())
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([sut.LineMatcherRegex],
                         visitor.visited_types)
        self.assertIs(instance,
                      ret_val)

    def test_raise_type_error_WHEN_visited_object_is_of_unknown_class(self):
        # ARRANGE #
        instance = UnknownLineMatcher()
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit(instance)
        # ASSERT #
        self.assertIsNot(visitor.visited_types,
                         'No visit method should have been executed.')

    pass


class AVisitorThatRecordsVisitedMethods(sut.LineMatcherStructureVisitor):
    def __init__(self):
        self.visited_types = []

    def visit_regex(self, matcher: sut.LineMatcherRegex):
        self.visited_types.append(sut.LineMatcherRegex)
        return matcher


class UnknownLineMatcher(sut.LineMatcher):
    def matches(self, line: str) -> bool:
        raise NotImplementedError('this method should never be called')
