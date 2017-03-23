import unittest

from exactly_lib.test_case_file_structure import concrete_path_parts as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestPathPartVisitor)


class TestPathPartVisitor(unittest.TestCase):
    def test_visit_fixed_path(self):
        # ARRANGE #
        recording_visitor = _VisitorThatRegisterClassOfVisitMethod()
        path_suffix = sut.PathPartAsFixedPath('file name')
        # ACT #
        ret_val = recording_visitor.visit(path_suffix)
        # ASSERT #
        self.assertEqual([sut.PathPartAsFixedPath],
                         recording_visitor.visited_classes,
                         'The method for visiting a %s should have been invoked'
                         % str(sut.PathPartAsFixedPath))
        self.assertIs(path_suffix,
                      ret_val,
                      'Returns value from visitor')

    def test_visit_symbol_reference(self):
        # ARRANGE #
        recording_visitor = _VisitorThatRegisterClassOfVisitMethod()
        path_suffix = sut.PathPartAsStringSymbolReference('symbol_name')
        # ACT #
        ret_val = recording_visitor.visit(path_suffix)
        # ASSERT #
        self.assertEqual([sut.PathPartAsStringSymbolReference],
                         recording_visitor.visited_classes,
                         'The method for visiting a %s should have been invoked'
                         % str(sut.PathPartAsStringSymbolReference))
        self.assertIs(path_suffix,
                      ret_val,
                      'Returns value from visitor')

    def test_visit_invalid_object_should_raise_exception(self):
        # ARRANGE #
        recording_visitor = _VisitorThatRegisterClassOfVisitMethod()
        not_a_path_suffix = 'a string is not a sub class of ' + str(sut.PathPart)
        # ACT & ASSERT #
        with self.assertRaises(TypeError):
            recording_visitor.visit(not_a_path_suffix)


class _VisitorThatRegisterClassOfVisitMethod(sut.PathPartVisitor):
    def __init__(self):
        self.visited_classes = []

    def visit_fixed_path(self, path_suffix: sut.PathPartAsFixedPath):
        self.visited_classes.append(sut.PathPartAsFixedPath)
        return path_suffix

    def visit_symbol_reference(self, path_suffix: sut.PathPartAsStringSymbolReference):
        self.visited_classes.append(sut.PathPartAsStringSymbolReference)
        return path_suffix
