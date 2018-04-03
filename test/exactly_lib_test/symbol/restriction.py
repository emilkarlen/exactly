import unittest

from exactly_lib.symbol import restriction as sut
from exactly_lib.symbol.data import string_resolvers, file_ref_resolvers2
from exactly_lib.symbol.program import component_resolvers
from exactly_lib.symbol.program.command_resolver import CommandResolver
from exactly_lib.symbol.program.component_resolvers import ArgumentsResolver
from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsNothing
from exactly_lib.type_system.data.concrete_string_values import string_value_of_single_string
from exactly_lib.type_system.data.list_value import ListValue
from exactly_lib.type_system.logic.program.command_values import CommandValueForShell
from exactly_lib.type_system.value_type import TypeCategory, ValueType
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.symbol.data.test_resources.list_values import ListResolverTestImplForConstantListValue
from exactly_lib_test.symbol.test_resources.command_resolvers import CommandDriverResolverForConstantTestImpl
from exactly_lib_test.symbol.test_resources.file_matcher import FileMatcherResolverConstantTestImpl
from exactly_lib_test.symbol.test_resources.line_matcher import LineMatcherResolverConstantTestImpl
from exactly_lib_test.symbol.test_resources.lines_transformer import LinesTransformerResolverConstantTestImpl
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.type_system.data.test_resources.file_matcher import FileMatcherThatSelectsAllFilesTestImpl
from exactly_lib_test.type_system.logic.test_resources.values import FakeLinesTransformer, \
    LineMatcherNotImplementedTestImpl


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestElementTypeRestriction),
        unittest.makeSuite(TestValueTypeRestriction),
    ])


class TestElementTypeRestriction(unittest.TestCase):
    element_type_2_resolver_of_type = {
        TypeCategory.DATA:
            string_resolvers.str_constant('string value'),

        TypeCategory.LOGIC:
            FileMatcherResolverConstantTestImpl(FileMatcherThatSelectsAllFilesTestImpl()),
    }

    def test_satisfied_restriction(self):
        # ARRANGE #
        named_elements = empty_symbol_table()
        for expected_element_type in TypeCategory:
            container_of_resolver = container(self.element_type_2_resolver_of_type[expected_element_type])
            with self.subTest(element_type=str(expected_element_type)):
                restriction_to_check = sut.TypeCategoryRestriction(expected_element_type)
                # ACT
                error_message = restriction_to_check.is_satisfied_by(named_elements,
                                                                     'name of element',
                                                                     container_of_resolver)
                # ASSERT #
                self.assertIsNone(error_message)

    def test_dissatisfied_restriction(self):
        # ARRANGE #
        cases = {
            TypeCategory.DATA: TypeCategory.LOGIC,

            TypeCategory.LOGIC: TypeCategory.DATA,
        }

        named_elements = empty_symbol_table()
        for expected_element_type, unexpected_element_type in cases.items():
            container_of_unexpected = container(self.element_type_2_resolver_of_type[unexpected_element_type])
            with self.subTest(expected_element_type=str(expected_element_type),
                              unexpected_element_type=str(unexpected_element_type)):
                restriction_to_check = sut.TypeCategoryRestriction(expected_element_type)
                # ACT
                error_message = restriction_to_check.is_satisfied_by(named_elements,
                                                                     'name of element',
                                                                     container_of_unexpected)
                # ASSERT #
                self.assertIsNotNone(error_message)


class TestValueTypeRestriction(unittest.TestCase):
    value_type_2_resolver_of_type = {

        ValueType.STRING:
            string_resolvers.str_constant('string value'),

        ValueType.LIST:
            ListResolverTestImplForConstantListValue(ListValue([])),

        ValueType.PATH:
            file_ref_resolvers2.constant(file_refs.rel_sandbox(RelSdsOptionType.REL_ACT, PathPartAsNothing())),

        ValueType.LINE_MATCHER:
            LineMatcherResolverConstantTestImpl(LineMatcherNotImplementedTestImpl()),

        ValueType.FILE_MATCHER:
            FileMatcherResolverConstantTestImpl(FileMatcherThatSelectsAllFilesTestImpl()),

        ValueType.LINES_TRANSFORMER:
            LinesTransformerResolverConstantTestImpl(FakeLinesTransformer(), []),

        ValueType.PROGRAM:
            ProgramResolver(
                CommandResolver(CommandDriverResolverForConstantTestImpl(
                    CommandValueForShell(string_value_of_single_string('the shell command line'))),
                    ArgumentsResolver(ListResolverTestImplForConstantListValue(ListValue([])))
                ),
                component_resolvers.no_stdin()
            ),
    }

    def test_satisfied_restriction(self):
        # ARRANGE #
        named_elements = empty_symbol_table()
        for expected_value_type in ValueType:
            container_of_resolver = container(self.value_type_2_resolver_of_type[expected_value_type])
            with self.subTest(element_type=str(expected_value_type)):
                restriction_to_check = sut.ValueTypeRestriction(expected_value_type)
                # ACT
                error_message = restriction_to_check.is_satisfied_by(named_elements,
                                                                     'name of element',
                                                                     container_of_resolver)
                # ASSERT #
                self.assertIsNone(error_message)

    def test_dissatisfied_restriction(self):
        # ARRANGE #
        cases = {
            ValueType.STRING: ValueType.LIST,
            ValueType.LIST: ValueType.PATH,
            ValueType.PATH: ValueType.FILE_MATCHER,
            ValueType.FILE_MATCHER: ValueType.LINES_TRANSFORMER,
            ValueType.LINES_TRANSFORMER: ValueType.STRING,
            ValueType.PROGRAM: ValueType.LINES_TRANSFORMER,
        }

        named_elements = empty_symbol_table()
        for expected_value_type, unexpected_value_type in cases.items():
            container_of_unexpected = container(self.value_type_2_resolver_of_type[unexpected_value_type])
            with self.subTest(expected_element_type=str(expected_value_type),
                              unexpected_element_type=str(unexpected_value_type)):
                restriction_to_check = sut.ValueTypeRestriction(expected_value_type)
                # ACT
                error_message = restriction_to_check.is_satisfied_by(named_elements,
                                                                     'name of element',
                                                                     container_of_unexpected)
                # ASSERT #
                self.assertIsNotNone(error_message)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
