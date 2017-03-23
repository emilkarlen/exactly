import unittest

from exactly_lib.test_case_file_structure import file_ref as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestPathSuffixVisitor)


class TestPathSuffixVisitor(unittest.TestCase):
    def test_visit_fixed_path(self):
        # ARRANGE #
        recording_visitor = VisitorThatRegisterClassOfVisitMethod()
        path_suffix = sut.PathSuffixAsFixedPath('file name')
        # ACT #
        ret_val = recording_visitor.visit(path_suffix)
        # ASSERT #
        self.assertEqual([sut.PathSuffixAsFixedPath],
                         recording_visitor.visited_classes,
                         'The method for visiting a %s should have been invoked'
                         % str(sut.PathSuffixAsFixedPath))
        self.assertIs(path_suffix,
                      ret_val,
                      'Returns value from visitor')

    def test_visit_symbol_reference(self):
        # ARRANGE #
        recording_visitor = VisitorThatRegisterClassOfVisitMethod()
        path_suffix = sut.PathSuffixAsStringSymbolReference('symbol_name')
        # ACT #
        ret_val = recording_visitor.visit(path_suffix)
        # ASSERT #
        self.assertEqual([sut.PathSuffixAsStringSymbolReference],
                         recording_visitor.visited_classes,
                         'The method for visiting a %s should have been invoked'
                         % str(sut.PathSuffixAsStringSymbolReference))
        self.assertIs(path_suffix,
                      ret_val,
                      'Returns value from visitor')

    def test_visit_invalid_object_should_raise_exception(self):
        # ARRANGE #
        recording_visitor = VisitorThatRegisterClassOfVisitMethod()
        not_a_path_suffix = 'a string is not a sub class of ' + str(sut.PathSuffix)
        # ACT & ASSERT #
        with self.assertRaises(TypeError):
            recording_visitor.visit(not_a_path_suffix)


class VisitorThatRegisterClassOfVisitMethod(sut.PathSuffixVisitor):
    def __init__(self):
        self.visited_classes = []

    def visit_fixed_path(self, path_suffix: sut.PathSuffixAsFixedPath):
        self.visited_classes.append(sut.PathSuffixAsFixedPath)
        return path_suffix

    def visit_symbol_reference(self, path_suffix: sut.PathSuffixAsStringSymbolReference):
        self.visited_classes.append(sut.PathSuffixAsStringSymbolReference)
        return path_suffix
