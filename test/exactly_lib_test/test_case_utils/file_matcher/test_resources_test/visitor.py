import re
import unittest

from exactly_lib.test_case_utils.file_matcher import file_matchers as sut
from exactly_lib.test_case_utils.file_matcher.impl.file_type import FileMatcherType
from exactly_lib.test_case_utils.file_matcher.impl.name_glob_pattern import FileMatcherNameGlobPattern
from exactly_lib.test_case_utils.file_matcher.impl.name_regex import FileMatcherBaseNameRegExPattern
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherModel
from exactly_lib_test.test_case_utils.file_matcher.test_resources import visitor


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestFileMatcherStructureVisitor)


class TestFileMatcherStructureVisitor(unittest.TestCase):
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

    def test_visit_name_glob_pattern(self):
        # ARRANGE #
        instance = FileMatcherNameGlobPattern('glob pattern')
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([FileMatcherNameGlobPattern],
                         visitor.visited_types)
        self.assertIs(instance,
                      ret_val)

    def test_visit_name_reg_ex_pattern(self):
        # ARRANGE #
        instance = FileMatcherBaseNameRegExPattern(re.compile('reg-ex pattern'))
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([FileMatcherBaseNameRegExPattern],
                         visitor.visited_types)
        self.assertIs(instance,
                      ret_val)

    def test_visit_type(self):
        # ARRANGE #
        instance = FileMatcherType(FileType.REGULAR)
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([FileMatcherType],
                         visitor.visited_types)
        self.assertIs(instance,
                      ret_val)

    def test_visit_and(self):
        # ARRANGE #
        instance = sut.FileMatcherAnd([])
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([sut.FileMatcherAnd],
                         visitor.visited_types)
        self.assertIs(instance,
                      ret_val)

    def test_visit_not(self):
        # ARRANGE #
        instance = sut.FileMatcherNot(sut.FileMatcherConstant(False))
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([sut.FileMatcherNot],
                         visitor.visited_types)
        self.assertIs(instance,
                      ret_val)

    def test_visit_or(self):
        # ARRANGE #
        instance = sut.FileMatcherOr([])
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([sut.FileMatcherOr],
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


class AVisitorThatRecordsVisitedMethods(visitor.FileMatcherStructureVisitor):
    def __init__(self):
        self.visited_types = []

    def visit_constant(self, matcher: sut.FileMatcherConstant):
        self.visited_types.append(sut.FileMatcherConstant)
        return matcher

    def visit_name_glob_pattern(self, matcher: FileMatcherNameGlobPattern):
        self.visited_types.append(FileMatcherNameGlobPattern)
        return matcher

    def visit_name_reg_ex_pattern(self, matcher: FileMatcherBaseNameRegExPattern):
        self.visited_types.append(FileMatcherBaseNameRegExPattern)
        return matcher

    def visit_type(self, matcher: FileMatcherType):
        self.visited_types.append(FileMatcherType)
        return matcher

    def visit_not(self, matcher: sut.FileMatcherNot):
        self.visited_types.append(sut.FileMatcherNot)
        return matcher

    def visit_and(self, matcher: sut.FileMatcherAnd):
        self.visited_types.append(sut.FileMatcherAnd)
        return matcher

    def visit_or(self, matcher: sut.FileMatcherOr):
        self.visited_types.append(sut.FileMatcherOr)
        return matcher


class UnknownFileMatcher(FileMatcher):
    @property
    def name(self) -> str:
        return str(type(self))

    @property
    def option_description(self) -> str:
        return str(type(self))

    def matches(self, model: FileMatcherModel) -> bool:
        raise NotImplementedError('this method should never be called')
