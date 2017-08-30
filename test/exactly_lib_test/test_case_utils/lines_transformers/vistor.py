import re
import unittest

import exactly_lib.test_case_utils.lines_transformers.transformers as sut
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib_test.type_system_values.logic.test_resources import FakeLinesTransformer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFileTransformerStructureVisitor),
    ])


class TestFileTransformerStructureVisitor(unittest.TestCase):
    def test_visit_identity(self):
        # ARRANGE #
        instance = sut.IdentityLinesTransformer()
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([sut.IdentityLinesTransformer],
                         visitor.visited_types)
        self.assertIs(instance, ret_val)

    def test_visit_sequence(self):
        # ARRANGE #
        instance = sut.SequenceLinesTransformer([])
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([sut.SequenceLinesTransformer],
                         visitor.visited_types)
        self.assertIs(instance, ret_val)

    def test_visit_replace(self):
        # ARRANGE #
        instance = sut.ReplaceLinesTransformer(re.compile('pattern'), 'replacement')
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([sut.ReplaceLinesTransformer],
                         visitor.visited_types)
        self.assertIs(instance, ret_val)

    def test_visit_custom(self):
        # ARRANGE #
        instance = MyCustomTransformer()
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([sut.CustomLinesTransformer],
                         visitor.visited_types)
        self.assertIs(instance, ret_val)

    def test_raise_type_error_WHEN_visited_object_is_of_unknown_class(self):
        # ARRANGE #
        instance = FakeLinesTransformer()
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

    def visit_identity(self, transformer: sut.IdentityLinesTransformer):
        self.visited_types.append(sut.IdentityLinesTransformer)
        return transformer

    def visit_sequence(self, transformer: sut.SequenceLinesTransformer):
        self.visited_types.append(sut.SequenceLinesTransformer)
        return transformer

    def visit_replace(self, transformer: sut.ReplaceLinesTransformer):
        self.visited_types.append(sut.ReplaceLinesTransformer)
        return transformer

    def visit_custom(self, transformer: sut.CustomLinesTransformer):
        self.visited_types.append(sut.CustomLinesTransformer)
        return transformer


class MyCustomTransformer(sut.CustomLinesTransformer):
    def __init__(self):
        super().__init__('my custom transformer')

    def transform(self, tcds: HomeAndSds, lines: iter) -> iter:
        return iter
