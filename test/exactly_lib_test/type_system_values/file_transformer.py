import unittest

from exactly_lib.type_system_values import file_transformer as sut


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
        self.assertEqual([sut.CustomFileTransformer],
                         visitor.visited_types)
        self.assertIs(instance, ret_val)

    def test_visit_identity(self):
        # ARRANGE #
        instance = sut.IdentityFileTransformer()
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(instance)
        # ASSERT #
        self.assertEqual([sut.IdentityFileTransformer],
                         visitor.visited_types)
        self.assertIs(instance, ret_val)

    def test_raise_type_error_WHEN_visited_object_is_of_unknown_class(self):
        # ARRANGE #
        instance = 'A value of a type that is not a ' + str(sut.FileTransformer)
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit(instance)
        # ASSERT #
        self.assertIsNot(visitor.visited_types,
                         'No visit method should have been executed.')

    pass


class AVisitorThatRecordsVisitedMethods(sut.FileTransformerStructureVisitor):
    def __init__(self):
        self.visited_types = []

    def visit_custom(self, selectors: sut.CustomFileTransformer):
        self.visited_types.append(sut.CustomFileTransformer)
        return selectors

    def visit_identity(self, selectors: sut.IdentityFileTransformer):
        self.visited_types.append(sut.IdentityFileTransformer)
        return selectors


class MyCustomTransformer(sut.CustomFileTransformer):
    def __init__(self):
        super().__init__('my custom transformer')

    def transform(self, lines: iter) -> iter:
        return iter
