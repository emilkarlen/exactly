import unittest

from exactly_lib.test_case_utils.file_selectors import file_selectors as sut
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.util.dir_contents_selection import Selectors


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFileSelectorStructureVisitor),
    ])


class TestFileSelectorStructureVisitor(unittest.TestCase):
    def test_visit_selectors(self):
        # ARRANGE #
        instance = sut.FileMatcherFromSelectors(Selectors())
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([Selectors],
                         visitor.visited_types)
        self.assertIs(instance.selectors,
                      ret_val)

    def test_raise_type_error_WHEN_visited_object_is_of_unknown_class(self):
        # ARRANGE #
        instance = 'A value of a type that is not a ' + str(FileMatcher)
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit(instance)
        # ASSERT #
        self.assertIsNot(visitor.visited_types,
                         'No visit method should have been executed.')

    pass


class AVisitorThatRecordsVisitedMethods(sut.FileSelectorStructureVisitor):
    def __init__(self):
        self.visited_types = []

    def visit_selectors(self, selectors: Selectors):
        self.visited_types.append(Selectors)
        return selectors
