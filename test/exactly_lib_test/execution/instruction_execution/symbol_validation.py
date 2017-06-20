import unittest

from exactly_lib.execution.instruction_execution import symbol_validation as sut
from exactly_lib.execution.instruction_execution.single_instruction_executor import PartialControlledFailureEnum
from exactly_lib.symbol import symbol_usage as su
from exactly_lib.symbol import value_structure as vs
from exactly_lib.symbol.concrete_restrictions import NoRestriction, ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.string_resolver import string_constant
from exactly_lib.symbol.value_resolvers.file_ref_with_symbol import rel_symbol
from exactly_lib.symbol.value_resolvers.path_part_resolvers import PathPartResolverAsFixedPath
from exactly_lib.symbol.value_restriction import ValueRestriction
from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import singleton_symbol_table, empty_symbol_table, Entry
from exactly_lib_test.symbol.test_resources.symbol_utils import file_ref_value_container, \
    file_ref_resolver_container


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSymbolReference),
        unittest.makeSuite(TestSymbolDefinition),
        unittest.makeSuite(TestValidationOfList),
    ])


class TestSymbolReference(unittest.TestCase):
    def test_WHEN_referenced_symbol_not_in_symbol_table_THEN_validation_error(self):
        # ARRANGE #
        symbol_table = empty_symbol_table()
        symbol_usage = su.SymbolReference('undefined', ReferenceRestrictionsOnDirectAndIndirect(NoRestriction()))
        # ACT #
        actual = sut.validate_symbol_usage(symbol_usage, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION,
                      actual.status)

    def test_WHEN_referenced_symbol_is_in_symbol_table_but_does_not_satisfy_value_restriction_THEN_validation_error(
            self):
        # ARRANGE #
        symbol_table = singleton_symbol_table(string_entry('val_name', 'symbol string'))
        symbol_usage = su.SymbolReference('val_name',
                                          ReferenceRestrictionsOnDirectAndIndirect(RestrictionThatCannotBeSatisfied()))
        # ACT #
        actual = sut.validate_symbol_usage(symbol_usage, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION,
                      actual.status)

    def test_WHEN_referenced_symbol_is_in_symbol_table_and_satisfies_value_restriction_THEN_no_error(self):
        # ARRANGE #
        symbol_table = singleton_symbol_table(string_entry('val_name', 'value string'))
        symbol_usage = su.SymbolReference('val_name',
                                          ReferenceRestrictionsOnDirectAndIndirect(RestrictionThatIsAlwaysSatisfied()))
        # ACT #
        actual = sut.validate_symbol_usage(symbol_usage, symbol_table)
        self.assertIsNone(actual, 'result should indicate success')


class TestSymbolDefinition(unittest.TestCase):
    def test_WHEN_defined_symbol_is_in_symbol_table_THEN_validation_error(self):
        # ARRANGE #
        symbol_table = singleton_symbol_table(string_entry('already-defined'))
        symbol_usage = symbol_of('already-defined')
        # ACT #
        actual = sut.validate_symbol_usage(symbol_usage, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION,
                      actual.status)

    def test_WHEN_defined_symbol_not_in_symbol_table_THEN_None_and_added_to_symbol_table(self):
        # ARRANGE #
        symbol_table = singleton_symbol_table(string_entry('other'))
        symbol_usage = symbol_of('undefined')
        # ACT #
        actual = sut.validate_symbol_usage(symbol_usage, symbol_table)
        self.assertIsNone(actual, 'return value for indicating')
        self.assertTrue(symbol_table.contains('undefined'),
                        'definition should be added to symbol table')
        self.assertTrue(symbol_table.contains('other'),
                        'definition in symbol table before definition should remain there')

    def test_WHEN_defined_symbol_not_in_symbol_table_but_referenced_symbols_not_in_table_THEN_validation_error(self):
        # ARRANGE #
        symbol_table = singleton_symbol_table(string_entry('OTHER'))
        symbol_usage = su.SymbolDefinition(
            'UNDEFINED',
            file_ref_resolver_container(
                rel_symbol(su.SymbolReference('REFERENCED',
                                              ReferenceRestrictionsOnDirectAndIndirect(
                                                  RestrictionThatIsAlwaysSatisfied())),
                           PathPartResolverAsFixedPath('file-name'))))
        # ACT #
        actual = sut.validate_symbol_usage(symbol_usage, symbol_table)
        self.assertIsNotNone(actual, 'return value for indicating error')

    def test_WHEN_defined_symbol_not_in_table_but_referenced_symbol_in_table_does_not_satisfy_restriction_THEN_error(
            self):
        # ARRANGE #
        referenced_entry = string_entry('REFERENCED')
        symbol_table = singleton_symbol_table(referenced_entry)
        symbol_usage_to_check = su.SymbolDefinition(
            'UNDEFINED',
            file_ref_resolver_container(
                rel_symbol(su.SymbolReference('REFERENCED',
                                              ReferenceRestrictionsOnDirectAndIndirect(
                                                  RestrictionThatCannotBeSatisfied())),
                           PathPartResolverAsFixedPath('file-name'))))
        # ACT #
        actual = sut.validate_symbol_usage(symbol_usage_to_check, symbol_table)
        # ASSERT #
        self.assertIsNotNone(actual, 'return value for indicating error')

    def test_WHEN_defined_symbol_not_in_symbol_table_and_referenced_symbol_is_in_table_and_satisfies_restriction_THEN_ok(
            self):
        # ARRANGE #
        referenced_entry = string_entry('REFERENCED')
        symbol_table = singleton_symbol_table(referenced_entry)
        symbol_usage_to_check = su.SymbolDefinition(
            'UNDEFINED',
            file_ref_resolver_container(
                rel_symbol(su.SymbolReference('REFERENCED',
                                              ReferenceRestrictionsOnDirectAndIndirect(
                                                  RestrictionThatIsAlwaysSatisfied())),
                           PathPartResolverAsFixedPath('file-name'))))
        # ACT #
        actual = sut.validate_symbol_usage(symbol_usage_to_check, symbol_table)
        # ASSERT #
        self.assertIsNone(actual, 'return value for indicating success')
        self.assertTrue(symbol_table.contains('UNDEFINED'),
                        'definition should have been added')


class TestValidationOfList(unittest.TestCase):
    def test_WHEN_no_usages_to_validate_THEN_validation_ok(
            self):
        # ARRANGE #
        symbol_table = empty_symbol_table()
        symbol_usages = []
        # ACT #
        actual = sut.validate_symbol_usages(symbol_usages, symbol_table)
        self.assertIsNone(actual, 'result should indicate ok')

    def test_WHEN_all_usages_are_valid_THEN_validation_ok(
            self):
        # ARRANGE #
        symbol_table = empty_symbol_table()
        valid_definition = symbol_of('symbol')
        valid__reference = su.SymbolReference('symbol', ReferenceRestrictionsOnDirectAndIndirect(NoRestriction()))
        symbol_usages = [
            valid_definition,
            valid__reference,
        ]
        # ACT #
        actual = sut.validate_symbol_usages(symbol_usages, symbol_table)
        self.assertIsNone(actual, 'result should indicate ok')

    def test_WHEN_2nd_element_fails_to_validate_THEN_validation_error(self):
        # ARRANGE #
        symbol_table = empty_symbol_table()
        valid_definition = symbol_of('name-of-definition')
        invalid__reference = su.SymbolReference('undefined', ReferenceRestrictionsOnDirectAndIndirect(NoRestriction()))
        symbol_usages = [
            valid_definition,
            invalid__reference,
        ]
        # ACT #
        actual = sut.validate_symbol_usages(symbol_usages, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION,
                      actual.status)


def symbol_of(name: str) -> su.SymbolDefinition:
    return su.SymbolDefinition(name,
                               vs.ValueContainer(Line(1, 'source code'),
                                                 string_constant('string value')))


def file_ref_entry(name: str, file_ref: FileRef) -> Entry:
    return Entry(name, file_ref_value_container(file_ref))


def string_entry(name: str, value: str = 'string value') -> Entry:
    return Entry(name,
                 vs.ValueContainer(Line(1, 'source code'),
                                   string_constant(value)))


def _path_relativity_variants_with_accepted(accepted: RelOptionType) -> PathRelativityVariants:
    return PathRelativityVariants({accepted}, False)


class RestrictionThatCannotBeSatisfied(ValueRestriction):
    def is_satisfied_by(self,
                        symbol_table: vs.SymbolTable,
                        symbol_name: str,
                        value: vs.ValueContainer) -> str:
        return 'unconditional error'


class RestrictionThatIsAlwaysSatisfied(ValueRestriction):
    def is_satisfied_by(self,
                        symbol_table: vs.SymbolTable,
                        symbol_name: str,
                        value: vs.ValueContainer) -> str:
        return None


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
