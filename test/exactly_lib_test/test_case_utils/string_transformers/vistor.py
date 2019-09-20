import re
import unittest
from typing import Iterable

from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherConstant
from exactly_lib.test_case_utils.string_transformer.impl import select, replace
from exactly_lib.test_case_utils.string_transformer.transformer_visitor import StringTransformerStructureVisitor
from exactly_lib.type_system.logic import string_transformer
from exactly_lib_test.type_system.logic.test_resources.values import FakeStringTransformer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestStringTransformerStructureVisitor),
    ])


class TestStringTransformerStructureVisitor(unittest.TestCase):
    def test_visit_identity(self):
        # ARRANGE #
        instance = string_transformer.IdentityStringTransformer()
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([string_transformer.IdentityStringTransformer],
                         visitor.visited_types)
        self.assertIs(instance, ret_val)

    def test_visit_sequence(self):
        # ARRANGE #
        instance = string_transformer.SequenceStringTransformer([])
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([string_transformer.SequenceStringTransformer],
                         visitor.visited_types)
        self.assertIs(instance, ret_val)

    def test_visit_replace(self):
        # ARRANGE #
        instance = replace.ReplaceStringTransformer(re.compile('pattern'), 'replacement')
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([replace.ReplaceStringTransformer],
                         visitor.visited_types)
        self.assertIs(instance, ret_val)

    def test_visit_select(self):
        # ARRANGE #
        instance = select.SelectStringTransformer(LineMatcherConstant(True))
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([select.SelectStringTransformer],
                         visitor.visited_types)
        self.assertIs(instance, ret_val)

    def test_visit_custom(self):
        # ARRANGE #
        instance = MyCustomTransformer()
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([string_transformer.CustomStringTransformer],
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


class AVisitorThatRecordsVisitedMethods(StringTransformerStructureVisitor):
    def __init__(self):
        self.visited_types = []

    def visit_identity(self, transformer: string_transformer.IdentityStringTransformer):
        self.visited_types.append(string_transformer.IdentityStringTransformer)
        return transformer

    def visit_sequence(self, transformer: string_transformer.SequenceStringTransformer):
        self.visited_types.append(string_transformer.SequenceStringTransformer)
        return transformer

    def visit_replace(self, transformer: replace.ReplaceStringTransformer):
        self.visited_types.append(replace.ReplaceStringTransformer)
        return transformer

    def visit_select(self, transformer: select.SelectStringTransformer):
        self.visited_types.append(select.SelectStringTransformer)
        return transformer

    def visit_custom(self, transformer: string_transformer.CustomStringTransformer):
        self.visited_types.append(string_transformer.CustomStringTransformer)
        return transformer


class MyCustomTransformer(string_transformer.CustomStringTransformer):
    def __init__(self):
        super().__init__()

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return iter
