import unittest

from exactly_lib.execution.impl import symbol_validation as sut
from exactly_lib.execution.impl.single_instruction_executor import PartialControlledFailureEnum
from exactly_lib.symbol import resolver_structure as vs, symbol_usage as su
from exactly_lib.symbol.data import file_ref_resolvers, path_part_resolvers
from exactly_lib.symbol.data import string_resolvers
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.data.value_restriction import ValueRestriction
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.util.line_source import single_line_sequence
from exactly_lib.util.symbol_table import singleton_symbol_table, empty_symbol_table, Entry
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restrictions import \
    unconditionally_unsatisfied_reference_restrictions, unconditionally_satisfied_reference_restrictions
from exactly_lib_test.symbol.data.test_resources.data_symbol_utils import file_ref_constant_container, \
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
        symbol_usage = su.SymbolReference('undefined', unconditionally_satisfied_reference_restrictions())
        # ACT #
        actual = sut.validate_symbol_usage(symbol_usage, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION_ERROR,
                      actual.status)

    def test_WHEN_referenced_symbol_is_in_symbol_table_but_does_not_satisfy_value_restriction_THEN_validation_error(
            self):
        # ARRANGE #
        symbol_table = singleton_symbol_table(string_entry('val_name', 'symbol string'))
        symbol_usage = su.SymbolReference('val_name',
                                          unconditionally_unsatisfied_reference_restrictions())
        # ACT #
        actual = sut.validate_symbol_usage(symbol_usage, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION_ERROR,
                      actual.status)

    def test_WHEN_referenced_symbol_is_in_symbol_table_and_satisfies_value_restriction_THEN_no_error(self):
        # ARRANGE #
        symbol_table = singleton_symbol_table(string_entry('val_name', 'value string'))
        symbol_usage = su.SymbolReference('val_name',
                                          ReferenceRestrictionsOnDirectAndIndirect(
                                              RestrictionThatIsAlwaysSatisfied()))
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
        self.assertIs(PartialControlledFailureEnum.VALIDATION_ERROR,
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
                file_ref_resolvers.rel_symbol(su.SymbolReference('REFERENCED',
                                                                 ReferenceRestrictionsOnDirectAndIndirect(
                                                                      RestrictionThatIsAlwaysSatisfied())),
                                              path_part_resolvers.from_constant_str('file-name'))))
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
                file_ref_resolvers.rel_symbol(su.SymbolReference('REFERENCED',
                                                                 unconditionally_unsatisfied_reference_restrictions()),
                                              path_part_resolvers.from_constant_str('file-name'))))
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
                file_ref_resolvers.rel_symbol(su.SymbolReference('REFERENCED',
                                                                 ReferenceRestrictionsOnDirectAndIndirect(
                                                                      RestrictionThatIsAlwaysSatisfied())),
                                              path_part_resolvers.from_constant_str('file-name'))))
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
        valid__reference = su.SymbolReference('symbol', unconditionally_satisfied_reference_restrictions())
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
        invalid__reference = su.SymbolReference('undefined', unconditionally_satisfied_reference_restrictions())
        symbol_usages = [
            valid_definition,
            invalid__reference,
        ]
        # ACT #
        actual = sut.validate_symbol_usages(symbol_usages, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION_ERROR,
                      actual.status)


def symbol_of(name: str) -> su.SymbolDefinition:
    return su.SymbolDefinition(name,
                               vs.SymbolContainer(string_resolvers.str_constant('string value'),
                                                  single_line_sequence(1, 'source code')))


def file_ref_entry(name: str, file_ref_value: FileRef) -> Entry:
    return Entry(name, file_ref_constant_container(file_ref_value))


def string_entry(name: str, constant: str = 'string value') -> Entry:
    return Entry(name,
                 vs.SymbolContainer(string_resolvers.str_constant(constant),
                                    single_line_sequence(1, 'source code')))


def _path_relativity_variants_with_accepted(accepted: RelOptionType) -> PathRelativityVariants:
    return PathRelativityVariants({accepted}, False)


class RestrictionThatIsAlwaysSatisfied(ValueRestriction):
    def is_satisfied_by(self,
                        symbol_table: vs.SymbolTable,
                        symbol_name: str,
                        container: vs.SymbolContainer) -> str:
        return None


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
