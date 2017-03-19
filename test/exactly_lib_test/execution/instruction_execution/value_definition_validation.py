import unittest

from exactly_lib.execution.instruction_execution import value_definition_validation as sut
from exactly_lib.execution.instruction_execution.single_instruction_executor import PartialControlledFailureEnum
from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.file_ref_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import singleton_symbol_table, empty_symbol_table, Entry
from exactly_lib.value_definition import value_structure as vs
from exactly_lib.value_definition.concrete_restrictions import NoRestriction
from exactly_lib.value_definition.concrete_values import StringValue
from exactly_lib.value_definition.file_ref_with_val_def import rel_value_definition
from exactly_lib.value_definition.value_structure import ValueRestriction
from exactly_lib_test.value_definition.test_resources.value_definition_utils import file_ref_value_container


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestValueReference),
        unittest.makeSuite(TestValueDefinition),
    ])


class TestValueReference(unittest.TestCase):
    def test_WHEN_referenced_value_not_in_symbol_table_THEN_validation_error(self):
        # ARRANGE #
        symbol_table = empty_symbol_table()
        value_usage = vs.ValueReference('undefined', NoRestriction())
        # ACT #
        actual = sut.validate_symbol_usages(value_usage, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION,
                      actual.status)

    def test_WHEN_referenced_value_is_in_symbol_table_but_does_not_satisfy_value_restriction_THEN_validation_error(
            self):
        # ARRANGE #
        symbol_table = singleton_symbol_table(string_entry('val_name', 'value string'))
        value_usage = vs.ValueReference('val_name',
                                        RestrictionThatCannotBeSatisfied())
        # ACT #
        actual = sut.validate_symbol_usages(value_usage, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION,
                      actual.status)

    def test_WHEN_referenced_value_is_in_symbol_table_and_satisfies_value_restriction_THEN_no_error(self):
        # ARRANGE #
        symbol_table = singleton_symbol_table(string_entry('val_name', 'value string'))
        value_usage = vs.ValueReference('val_name',
                                        RestrictionThatIsAlwaysSatisfied())
        # ACT #
        actual = sut.validate_symbol_usages(value_usage, symbol_table)
        self.assertIsNone(actual, 'result should indicate success')


class TestValueDefinition(unittest.TestCase):
    def test_WHEN_defined_value_is_in_symbol_table_THEN_validation_error(self):
        # ARRANGE #
        symbol_table = singleton_symbol_table(string_entry('already-defined'))
        value_usage = value_definition_of('already-defined')
        # ACT #
        actual = sut.validate_symbol_usages(value_usage, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION,
                      actual.status)

    def test_WHEN_defined_value_not_in_symbol_table_THEN_None_and_added_to_symbol_table(self):
        # ARRANGE #
        symbol_table = singleton_symbol_table(string_entry('other'))
        value_usage = value_definition_of('undefined')
        # ACT #
        actual = sut.validate_symbol_usages(value_usage, symbol_table)
        self.assertIsNone(actual, 'return value for indicating')
        self.assertTrue(symbol_table.contains('undefined'),
                        'definition should be added to symbol table')
        self.assertTrue(symbol_table.contains('other'),
                        'definition in symbol table before definition should remain there')

    def test_WHEN_defined_value_not_in_symbol_table_but_referenced_values_not_in_table_THEN_validation_error(self):
        # ARRANGE #
        symbol_table = singleton_symbol_table(string_entry('OTHER'))
        value_usage = vs.ValueDefinition(
            'UNDEFINED',
            file_ref_value_container(
                rel_value_definition(vs.ValueReference('REFERENCED', RestrictionThatIsAlwaysSatisfied()),
                                     'file-name')))
        # ACT #
        actual = sut.validate_symbol_usages(value_usage, symbol_table)
        self.assertIsNotNone(actual, 'return value for indicating error')

    def test_WHEN_defined_value_not_in_table_but_referenced_value_in_table_does_not_satisfy_restriction_THEN_error(
            self):
        # ARRANGE #
        referenced_entry = string_entry('REFERENCED')
        symbol_table = singleton_symbol_table(referenced_entry)
        value_usage_to_check = vs.ValueDefinition(
            'UNDEFINED',
            file_ref_value_container(
                rel_value_definition(vs.ValueReference('REFERENCED', RestrictionThatCannotBeSatisfied()),
                                     'file-name')))
        # ACT #
        actual = sut.validate_symbol_usages(value_usage_to_check, symbol_table)
        # ASSERT #
        self.assertIsNotNone(actual, 'return value for indicating error')

    def test_WHEN_defined_value_not_in_symbol_table_and_referenced_value_is_in_table_and_satisfies_restriction_THEN_ok(
            self):
        # ARRANGE #
        referenced_entry = string_entry('REFERENCED')
        symbol_table = singleton_symbol_table(referenced_entry)
        value_usage_to_check = vs.ValueDefinition(
            'UNDEFINED',
            file_ref_value_container(
                rel_value_definition(vs.ValueReference('REFERENCED', RestrictionThatIsAlwaysSatisfied()),
                                     'file-name')))
        # ACT #
        actual = sut.validate_symbol_usages(value_usage_to_check, symbol_table)
        # ASSERT #
        self.assertIsNone(actual, 'return value for indicating success')
        self.assertTrue(symbol_table.contains('UNDEFINED'),
                        'definition should have been added')


def value_definition_of(name: str) -> vs.ValueDefinition:
    return vs.ValueDefinition(name,
                              vs.ValueContainer(Line(1, 'source code'),
                                                 StringValue('string value')))


def file_ref_entry(name: str, file_ref: FileRef) -> Entry:
    return Entry(name, file_ref_value_container(file_ref))


def string_entry(name: str, value: str = 'string value') -> Entry:
    return Entry(name,
                 vs.ValueContainer(Line(1, 'source code'),
                                   StringValue(value)))


def _path_relativity_variants_with_accepted(accepted: RelOptionType) -> PathRelativityVariants:
    return PathRelativityVariants({accepted}, False)


class RestrictionThatCannotBeSatisfied(ValueRestriction):
    def is_satisfied_by(self,
                        symbol_table: vs.SymbolTable,
                        value: vs.Value) -> str:
        return 'unconditional error'


class RestrictionThatIsAlwaysSatisfied(ValueRestriction):
    def is_satisfied_by(self,
                        symbol_table: vs.SymbolTable,
                        value: vs.Value) -> str:
        return None


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
