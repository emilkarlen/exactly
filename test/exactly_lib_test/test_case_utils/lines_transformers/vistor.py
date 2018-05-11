import re
import unittest
from typing import Iterable

import exactly_lib.test_case_utils.string_transformer.transformers as sut
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherConstant
from exactly_lib.type_system.logic import lines_transformer
from exactly_lib_test.type_system.logic.test_resources.values import FakeStringTransformer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestLinesTransformerStructureVisitor),
    ])


class TestLinesTransformerStructureVisitor(unittest.TestCase):
    def test_visit_identity(self):
        # ARRANGE #
        instance = lines_transformer.IdentityStringTransformer()
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([lines_transformer.IdentityStringTransformer],
                         visitor.visited_types)
        self.assertIs(instance, ret_val)

    def test_visit_sequence(self):
        # ARRANGE #
        instance = lines_transformer.SequenceStringTransformer([])
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([lines_transformer.SequenceStringTransformer],
                         visitor.visited_types)
        self.assertIs(instance, ret_val)

    def test_visit_replace(self):
        # ARRANGE #
        instance = sut.ReplaceStringTransformer(re.compile('pattern'), 'replacement')
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([sut.ReplaceStringTransformer],
                         visitor.visited_types)
        self.assertIs(instance, ret_val)

    def test_visit_select(self):
        # ARRANGE #
        instance = sut.SelectStringTransformer(LineMatcherConstant(True))
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([sut.SelectStringTransformer],
                         visitor.visited_types)
        self.assertIs(instance, ret_val)

    def test_visit_custom(self):
        # ARRANGE #
        instance = MyCustomTransformer()
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([lines_transformer.CustomStringTransformer],
                         visitor.visited_types)
        self.assertIs(instance, ret_val)

    def test_raise_type_error_WHEN_visited_object_is_of_unknown_class(self):
        # ARRANGE #
        instance = FakeStringTransformer()
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit(instance)
        # ASSERT #
        self.assertIsNot(visitor.visited_types,
                         'No visit method should have been executed.')

    pass


class AVisitorThatRecordsVisitedMethods(sut.LinesTransformerStructureVisitor):
    def __init__(self):
        self.visited_types = []

    def visit_identity(self, transformer: lines_transformer.IdentityStringTransformer):
        self.visited_types.append(lines_transformer.IdentityStringTransformer)
        return transformer

    def visit_sequence(self, transformer: lines_transformer.SequenceStringTransformer):
        self.visited_types.append(lines_transformer.SequenceStringTransformer)
        return transformer

    def visit_replace(self, transformer: sut.ReplaceStringTransformer):
        self.visited_types.append(sut.ReplaceStringTransformer)
        return transformer

    def visit_select(self, transformer: sut.SelectStringTransformer):
        self.visited_types.append(sut.SelectStringTransformer)
        return transformer

    def visit_custom(self, transformer: lines_transformer.CustomStringTransformer):
        self.visited_types.append(lines_transformer.CustomStringTransformer)
        return transformer


class MyCustomTransformer(lines_transformer.CustomStringTransformer):
    def __init__(self):
        super().__init__()

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return iter
