import unittest

from exactly_lib.test_case_file_structure import concrete_path_parts as sut
from exactly_lib.util import symbol_table as st
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.value_definition.test_resources.concrete_restriction_assertion import is_string_value_restriction
from exactly_lib_test.value_definition.test_resources.value_definition_utils import string_value_container
from exactly_lib_test.value_definition.test_resources.value_reference_assertions import equals_value_reference


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestPathPartAsFixedPath),
        unittest.makeSuite(TestPathPartAsStringSymbolReference),
        unittest.makeSuite(TestPathPartVisitor),
    ])


class TestPathPartAsFixedPath(unittest.TestCase):
    def test_file_name(self):
        # ARRANGE #
        path_part = sut.PathPartAsFixedPath('the file name')
        # ACT #
        actual = path_part.file_name
        # ASSERT #
        self.assertEqual('the file name',
                         actual,
                         'file name')

    def test_value_references(self):
        # ARRANGE #
        path_part = sut.PathPartAsFixedPath('the file name')
        # ACT #
        actual = path_part.value_references
        # ASSERT #
        self.assertEqual([],
                         actual,
                         'value references')

    def test_resolve(self):
        # ARRANGE #
        path_part = sut.PathPartAsFixedPath('the file name')
        # ACT #
        actual = path_part.resolve(st.empty_symbol_table())
        # ASSERT #
        self.assertEqual('the file name',
                         actual,
                         'resolved file name')


class TestPathPartAsStringSymbolReference(unittest.TestCase):
    def test_symbol_name(self):
        # ARRANGE #
        path_part = sut.PathPartAsStringSymbolReference('the symbol name')
        # ACT #
        actual = path_part.symbol_name
        # ASSERT #
        self.assertEqual('the symbol name',
                         actual,
                         'symbol name')

    def test_value_references(self):
        # ARRANGE #
        path_part = sut.PathPartAsStringSymbolReference('the symbol name')
        # ACT #
        actual = path_part.value_references
        # ASSERT #
        assertion = asrt.matches_sequence([
            equals_value_reference('the symbol name',
                                   is_string_value_restriction)
        ])
        assertion.apply_with_message(self, actual, 'value references')

    def test_resolve(self):
        # ARRANGE #
        path_part = sut.PathPartAsStringSymbolReference('the symbol name')
        symbol_table = st.singleton_symbol_table(st.Entry('the symbol name',
                                                          string_value_container('symbol value')))
        # ACT #
        actual = path_part.resolve(symbol_table)
        # ASSERT #
        self.assertEqual('symbol value',
                         actual,
                         'resolved file name')


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
