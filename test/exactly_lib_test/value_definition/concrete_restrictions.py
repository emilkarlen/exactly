import unittest

from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib.value_definition import concrete_restrictions as sut
from exactly_lib.value_definition.concrete_values import StringValue
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl
from exactly_lib_test.value_definition.test_resources.value_definition_utils import file_ref_value


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestNoRestriction),
        unittest.makeSuite(TestFileRefRelativityRestriction),
        unittest.makeSuite(TestValueRestrictionVisitor),
    ])


class TestNoRestriction(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        test_cases = [
            StringValue('string'),
            file_ref_value(),
        ]
        restriction = sut.NoRestriction()
        value_definitions = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                # ACT #
                actual = restriction.is_satisfied_by(value_definitions, value)
                # ASSERT #
                self.assertIsNone(actual)


class TestFileRefRelativityRestriction(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        test_cases = [
            file_ref_value(file_ref_test_impl(relativity=RelOptionType.REL_ACT)),
            file_ref_value(file_ref_test_impl(relativity=RelOptionType.REL_HOME)),
        ]
        restriction = sut.FileRefRelativityRestriction(PathRelativityVariants(
            {RelOptionType.REL_ACT, RelOptionType.REL_HOME, RelOptionType.REL_RESULT},
            False))
        value_definitions = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                # ACT #
                actual = restriction.is_satisfied_by(value_definitions, value)
                # ASSERT #
                self.assertIsNone(actual)

    def test_fail__relative_paths(self):
        # ARRANGE #
        test_cases = [
            file_ref_value(file_ref_test_impl(relativity=RelOptionType.REL_ACT)),
            file_ref_value(file_ref_test_impl(relativity=RelOptionType.REL_HOME)),
        ]
        restriction = sut.FileRefRelativityRestriction(PathRelativityVariants(
            {RelOptionType.REL_RESULT},
            False))
        value_definitions = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                # ACT #
                actual = restriction.is_satisfied_by(value_definitions, value)
                # ASSERT #
                self.assertIsNotNone(actual,
                                     'Result should denote failing validation')


class TestValueRestrictionVisitor(unittest.TestCase):
    def test_none(self):
        # ARRANGE #
        expected_return_value = 72
        visitor = _VisitorThatRegisterClassOfVisitMethod(expected_return_value)
        # ACT #
        actual_return_value = visitor.visit(sut.NoRestriction())
        # ASSERT #
        self.assertEquals([sut.NoRestriction],
                          visitor.visited_classes,
                          'visited classes')
        self.assertEquals(expected_return_value,
                          actual_return_value,
                          'return value')

    def test_string(self):
        # ARRANGE #
        expected_return_value = 87
        visitor = _VisitorThatRegisterClassOfVisitMethod(expected_return_value)
        # ACT #
        actual_return_value = visitor.visit(sut.StringRestriction())
        # ASSERT #
        self.assertEquals([sut.StringRestriction],
                          visitor.visited_classes,
                          'visited classes')
        self.assertEquals(expected_return_value,
                          actual_return_value,
                          'return value')

    def test_file_ref(self):
        # ARRANGE #
        expected_return_value = 69
        visitor = _VisitorThatRegisterClassOfVisitMethod(expected_return_value)
        # ACT #
        actual_return_value = visitor.visit(sut.FileRefRelativityRestriction(
            sut.PathRelativityVariants(set(), False)))
        # ASSERT #
        self.assertEquals([sut.FileRefRelativityRestriction],
                          visitor.visited_classes,
                          'visited classes')
        self.assertEquals(expected_return_value,
                          actual_return_value,
                          'return value')

    def test_visit_invalid_object_should_raise_exception(self):
        # ARRANGE #
        visitor = _VisitorThatRegisterClassOfVisitMethod("not used")
        non_concept = 'a string is not a sub class of ' + str(sut.ValueRestriction)
        # ACT & ASSERT #
        with self.assertRaises(TypeError):
            visitor.visit(non_concept)


class _VisitorThatRegisterClassOfVisitMethod(sut.ValueRestrictionVisitor):
    def __init__(self, return_value):
        self.visited_classes = []
        self.return_value = return_value

    def visit_none(self, x: sut.NoRestriction):
        self.visited_classes.append(sut.NoRestriction)
        return self.return_value

    def visit_string(self, x: sut.StringRestriction):
        self.visited_classes.append(sut.StringRestriction)
        return self.return_value

    def visit_file_ref_relativity(self, x: sut.FileRefRelativityRestriction):
        self.visited_classes.append(sut.FileRefRelativityRestriction)
        return self.return_value
