import unittest

import pathlib

from exactly_lib.test_case_utils.file_matcher import file_matchers as sut
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.util.dir_contents_selection import Selectors


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestFileMatcherStructureVisitor)


class TestFileMatcherStructureVisitor(unittest.TestCase):
    def test_visit_selectors(self):
        # ARRANGE #
        instance = sut.FileMatcherFromSelectors(Selectors())
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([sut.FileMatcherFromSelectors],
                         visitor.visited_types)
        self.assertIs(instance,
                      ret_val)

    def test_visit_constant(self):
        # ARRANGE #
        instance = sut.FileMatcherConstant(False)
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([sut.FileMatcherConstant],
                         visitor.visited_types)
        self.assertIs(instance,
                      ret_val)

    def test_raise_type_error_WHEN_visited_object_is_of_unknown_class(self):
        # ARRANGE #
        instance = UnknownFileMatcher()
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit(instance)
        # ASSERT #
        self.assertIsNot(visitor.visited_types,
                         'No visit method should have been executed.')

    pass


class AVisitorThatRecordsVisitedMethods(sut.FileMatcherStructureVisitor):
    def __init__(self):
        self.visited_types = []

    def visit_constant(self, matcher: sut.FileMatcherConstant):
        self.visited_types.append(sut.FileMatcherConstant)
        return matcher

    def visit_selectors(self, matcher: sut.FileMatcherFromSelectors):
        self.visited_types.append(sut.FileMatcherFromSelectors)
        return matcher


class UnknownFileMatcher(FileMatcher):
    def select_from(self, directory: pathlib.Path) -> iter:
        raise NotImplementedError('this method should never be called')

    def matches(self, path: pathlib.Path) -> bool:
        raise NotImplementedError('this method should never be called')
