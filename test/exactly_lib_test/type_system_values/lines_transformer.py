import unittest

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system_values import lines_transformer as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFileTransformerStructureVisitor),
    ])


class TestFileTransformerStructureVisitor(unittest.TestCase):
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

    def test_raise_type_error_WHEN_visited_object_is_of_unknown_class(self):
        # ARRANGE #
        instance = 'A value of a type that is not a ' + str(sut.LinesTransformer)
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

    def visit_custom(self, selectors: sut.CustomLinesTransformer):
        self.visited_types.append(sut.CustomLinesTransformer)
        return selectors

    def visit_identity(self, selectors: sut.IdentityLinesTransformer):
        self.visited_types.append(sut.IdentityLinesTransformer)
        return selectors


class MyCustomTransformer(sut.CustomLinesTransformer):
    def __init__(self):
        super().__init__('my custom transformer')

    def transform(self, tcds: HomeAndSds, lines: iter) -> iter:
        return iter
