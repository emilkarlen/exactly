import unittest

from exactly_lib.symbol.path_resolver import FileRefResolver
from exactly_lib.symbol.restriction import ValueRestriction
from exactly_lib.symbol.restrictions import value_restrictions as vr
from exactly_lib.symbol.string_resolver import string_constant
from exactly_lib.symbol.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestNoRestriction),
        unittest.makeSuite(TestStringRestriction),
        unittest.makeSuite(TestFileRefRelativityRestriction),
        unittest.makeSuite(TestValueRestrictionVisitor),
    ])


class TestNoRestriction(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        test_cases = [
            string_constant('string'),
            file_ref_constant_resolver(),
        ]
        restriction = vr.NoRestriction()
        symbols = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                container = symbol_utils.container(value)
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', container)
                # ASSERT #
                self.assertIsNone(actual)


class TestStringRestriction(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        test_cases = [
            string_constant('string'),
            string_constant(''),
        ]
        restriction = vr.StringRestriction()
        symbols = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                container = symbol_utils.container(value)
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', container)
                # ASSERT #
                self.assertIsNone(actual)

    def test_fail__not_a_string(self):
        # ARRANGE #
        test_cases = [
            file_ref_constant_resolver(),
        ]
        restriction = vr.StringRestriction()
        symbols = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                container = symbol_utils.container(value)
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', container)
                # ASSERT #
                self.assertIsNotNone(actual,
                                     'Result should denote failing validation')


class TestFileRefRelativityRestriction(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        test_cases = [
            FileRefConstant(file_ref_test_impl(relativity=RelOptionType.REL_ACT)),
            FileRefConstant(file_ref_test_impl(relativity=RelOptionType.REL_HOME)),
        ]
        restriction = vr.FileRefRelativityRestriction(
            PathRelativityVariants(
                {RelOptionType.REL_ACT, RelOptionType.REL_HOME, RelOptionType.REL_RESULT},
                False))
        symbols = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                container = symbol_utils.container(value)
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', container)
                # ASSERT #
                self.assertIsNone(actual)

    def test_fail__relative_paths(self):
        # ARRANGE #
        test_cases = [
            FileRefConstant(file_ref_test_impl(relativity=RelOptionType.REL_ACT)),
            FileRefConstant(file_ref_test_impl(relativity=RelOptionType.REL_HOME)),
        ]
        restriction = vr.FileRefRelativityRestriction(
            PathRelativityVariants(
                {RelOptionType.REL_RESULT},
                False))
        symbols = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                container = symbol_utils.container(value)
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', container)
                # ASSERT #
                self.assertIsNotNone(actual,
                                     'Result should denote failing validation')


class TestValueRestrictionVisitor(unittest.TestCase):
    def test_none(self):
        # ARRANGE #
        expected_return_value = 72
        visitor = _VisitorThatRegisterClassOfVisitMethod(expected_return_value)
        # ACT #
        actual_return_value = visitor.visit(vr.NoRestriction())
        # ASSERT #
        self.assertEqual([vr.NoRestriction],
                         visitor.visited_classes,
                         'visited classes')
        self.assertEqual(expected_return_value,
                         actual_return_value,
                         'return value')

    def test_string(self):
        # ARRANGE #
        expected_return_value = 87
        visitor = _VisitorThatRegisterClassOfVisitMethod(expected_return_value)
        # ACT #
        actual_return_value = visitor.visit(vr.StringRestriction())
        # ASSERT #
        self.assertEqual([vr.StringRestriction],
                         visitor.visited_classes,
                         'visited classes')
        self.assertEqual(expected_return_value,
                         actual_return_value,
                         'return value')

    def test_file_ref(self):
        # ARRANGE #
        expected_return_value = 69
        visitor = _VisitorThatRegisterClassOfVisitMethod(expected_return_value)
        # ACT #
        actual_return_value = visitor.visit(
            vr.FileRefRelativityRestriction(
                PathRelativityVariants(set(), False)))
        # ASSERT #
        self.assertEqual([vr.FileRefRelativityRestriction],
                         visitor.visited_classes,
                         'visited classes')
        self.assertEqual(expected_return_value,
                         actual_return_value,
                         'return value')

    def test_visit_invalid_object_should_raise_exception(self):
        # ARRANGE #
        visitor = _VisitorThatRegisterClassOfVisitMethod("not used")
        non_concept = 'a string is not a sub class of ' + str(ValueRestriction)
        # ACT & ASSERT #
        with self.assertRaises(TypeError):
            visitor.visit(non_concept)


class _VisitorThatRegisterClassOfVisitMethod(vr.ValueRestrictionVisitor):
    def __init__(self, return_value):
        self.visited_classes = []
        self.return_value = return_value

    def visit_none(self, x: vr.NoRestriction):
        self.visited_classes.append(vr.NoRestriction)
        return self.return_value

    def visit_string(self, x: vr.StringRestriction):
        self.visited_classes.append(vr.StringRestriction)
        return self.return_value

    def visit_file_ref_relativity(self,
                                  x: vr.FileRefRelativityRestriction):
        self.visited_classes.append(vr.FileRefRelativityRestriction)
        return self.return_value


def file_ref_constant_resolver() -> FileRefResolver:
    return FileRefConstant(file_ref_test_impl('file-name-rel-home',
                                              relativity=RelOptionType.REL_HOME))
