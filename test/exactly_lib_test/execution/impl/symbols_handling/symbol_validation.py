import pathlib
import unittest
from typing import Optional

from exactly_lib.common.err_msg.err_msg_w_fix_tip import ErrorMessageWithFixTip
from exactly_lib.execution.impl import symbol_validation as sut
from exactly_lib.execution.impl.single_instruction_executor import PartialControlledFailureEnum
from exactly_lib.section_document.source_location import FileLocationInfo, SourceLocationInfo
from exactly_lib.symbol import sdv_structure as rs
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.type_val_deps.sym_ref.data.data_value_restriction import ValueRestriction
from exactly_lib.type_val_deps.sym_ref.data.reference_restrictions import ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.type_val_deps.types.path import path_part_sdvs
from exactly_lib.type_val_deps.types.path import path_sdvs
from exactly_lib.util import line_source
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.type_val_deps.test_resources.any_.reference_restrictions import \
    reference_restrictions__unconditionally_unsatisfied, reference_restrictions__unconditionally_satisfied
from exactly_lib_test.type_val_deps.types.path.test_resources.path import PathSymbolContext
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringSymbolContext


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
        symbol_usage = SymbolReference('undefined', reference_restrictions__unconditionally_satisfied())
        # ACT #
        actual = sut.validate_symbol_usage(symbol_usage, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION_ERROR,
                      actual.status)

    def test_WHEN_referenced_symbol_is_in_symbol_table_but_does_not_satisfy_value_restriction_THEN_validation_error(
            self):
        # ARRANGE #
        symbol_table = StringSymbolContext.of_constant('val_name', 'symbol string').symbol_table
        symbol_usage = SymbolReference('val_name',
                                       reference_restrictions__unconditionally_unsatisfied())
        # ACT #
        actual = sut.validate_symbol_usage(symbol_usage, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION_ERROR,
                      actual.status)

    def test_WHEN_referenced_symbol_is_in_symbol_table_and_satisfies_value_restriction_THEN_no_error(self):
        # ARRANGE #
        symbol_table = StringSymbolContext.of_constant('val_name', 'value string').symbol_table
        symbol_reference = SymbolReference('val_name',
                                           ReferenceRestrictionsOnDirectAndIndirect(
                                               RestrictionThatIsAlwaysSatisfied()))
        # ACT #
        actual = sut.validate_symbol_usage(symbol_reference, symbol_table)
        self.assertIsNone(actual, 'result should indicate success')


class TestSymbolDefinition(unittest.TestCase):
    def test_WHEN_defined_symbol_is_in_symbol_table_THEN_validation_error(self):
        # ARRANGE #
        name = 'already-defined'
        symbol_table = StringSymbolContext.of_constant(name, 'arbitrary value').symbol_table
        symbol_definition = StringSymbolContext.of_constant(name, 'other value').definition
        # ACT #
        actual = sut.validate_symbol_usage(symbol_definition, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION_ERROR,
                      actual.status)

    def test_WHEN_defined_symbol_not_in_symbol_table_THEN_None_and_added_to_symbol_table(self):
        # ARRANGE #
        symbol_table = StringSymbolContext.of_constant('other', 'value').symbol_table
        symbol_definition = StringSymbolContext.of_constant('undefined', 'value').definition
        # ACT #
        actual = sut.validate_symbol_usage(symbol_definition, symbol_table)
        self.assertIsNone(actual, 'return value for indicating')
        self.assertTrue(symbol_table.contains('undefined'),
                        'definition should be added to symbol table')
        self.assertTrue(symbol_table.contains('other'),
                        'definition in symbol table before definition should remain there')

    def test_WHEN_defined_symbol_not_in_symbol_table_but_referenced_symbols_not_in_table_THEN_validation_error(self):
        # ARRANGE #
        symbol_table = StringSymbolContext.of_constant('OTHER', 'value').symbol_table
        symbol = PathSymbolContext.of_sdv(
            'UNDEFINED',
            path_sdvs.rel_symbol(SymbolReference('REFERENCED',
                                                 ReferenceRestrictionsOnDirectAndIndirect(
                                                     RestrictionThatIsAlwaysSatisfied())),
                                 path_part_sdvs.from_constant_str('file-name')))
        # ACT #
        actual = sut.validate_symbol_usage(symbol.definition, symbol_table)
        self.assertIsNotNone(actual, 'return value for indicating error')

    def test_WHEN_defined_symbol_not_in_table_but_referenced_symbol_in_table_does_not_satisfy_restriction_THEN_error(
            self):
        # ARRANGE #
        symbol_table = StringSymbolContext.of_constant('REFERENCED', 'value').symbol_table
        symbol = PathSymbolContext.of_sdv(
            'UNDEFINED',
            path_sdvs.rel_symbol(SymbolReference('REFERENCED',
                                                 reference_restrictions__unconditionally_unsatisfied()),
                                 path_part_sdvs.from_constant_str('file-name')))
        # ACT #
        actual = sut.validate_symbol_usage(symbol.definition, symbol_table)
        # ASSERT #
        self.assertIsNotNone(actual, 'return value for indicating error')

    def test_WHEN_defined_symbol_not_in_symbol_table_and_referenced_symbol_is_in_table_and_satisfies_restriction_THEN_ok(
            self):
        # ARRANGE #
        referenced_symbol = StringSymbolContext.of_constant('REFERENCED', 'value')
        symbol_table = referenced_symbol.symbol_table
        symbol = PathSymbolContext.of_sdv('UNDEFINED',
                                          path_sdvs.rel_symbol(
                                              SymbolReference('REFERENCED',
                                                              ReferenceRestrictionsOnDirectAndIndirect(
                                                                  RestrictionThatIsAlwaysSatisfied())),
                                              path_part_sdvs.from_constant_str('file-name')))
        # ACT #
        actual = sut.validate_symbol_usage(symbol.definition, symbol_table)
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
        valid_definition = StringSymbolContext.of_constant('symbol', 'value').definition
        valid__reference = SymbolReference('symbol', reference_restrictions__unconditionally_satisfied())
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
        valid_definition = StringSymbolContext.of_constant('name-of-definition', 'value').definition
        invalid__reference = SymbolReference('undefined', reference_restrictions__unconditionally_satisfied())
        symbol_usages = [
            valid_definition,
            invalid__reference,
        ]
        # ACT #
        actual = sut.validate_symbol_usages(symbol_usages, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION_ERROR,
                      actual.status)


def _path_relativity_variants_with_accepted(accepted: RelOptionType) -> PathRelativityVariants:
    return PathRelativityVariants({accepted}, False)


class RestrictionThatIsAlwaysSatisfied(ValueRestriction):
    def is_satisfied_by(self,
                        symbol_table: rs.SymbolTable,
                        symbol_name: str,
                        container: rs.SymbolContainer) -> Optional[ErrorMessageWithFixTip]:
        return None


_FL = FileLocationInfo(pathlib.Path('/'))


def single_line_sequence(line_number: int, line: str) -> SourceLocationInfo:
    return _FL.source_location_info_for(line_source.single_line_sequence(line_number, line))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
