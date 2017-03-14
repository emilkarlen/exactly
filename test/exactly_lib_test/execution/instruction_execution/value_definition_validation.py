import unittest

from exactly_lib.execution.instruction_execution import value_definition_validation as sut
from exactly_lib.execution.instruction_execution.single_instruction_executor import PartialControlledFailureEnum
from exactly_lib.test_case import file_refs
from exactly_lib.test_case.file_ref import FileRef
from exactly_lib.test_case.file_ref_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.util.symbol_table import singleton_symbol_table, empty_symbol_table, Entry
from exactly_lib.value_definition import value_definition_usage as vd
from exactly_lib_test.test_case.test_resources.value_definition import file_ref_value


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestValueReference),
        unittest.makeSuite(TestValueDefinition),
    ])


class TestValueReference(unittest.TestCase):
    def test_WHEN_referenced_value_not_in_symbol_table_THEN_validation_error(self):
        # ARRANGE #
        symbol_table = empty_symbol_table()
        value_usage = vd.ValueReference('undefined')
        # ACT #
        actual = sut.validate_pre_sds(value_usage, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION,
                      actual.status)

    def test_WHEN_referenced_value_in_symbol_table_has_invalid_relativity_THEN_validation_error(self):
        # ARRANGE #
        symbol_table = singleton_symbol_table(file_ref_entry('file_ref', file_refs.rel_home('home-file')))
        value_usage = vd.ValueReferenceOfPath('file_ref',
                                              PathRelativityVariants({RelOptionType.REL_ACT,
                                                                      RelOptionType.REL_TMP},
                                                                     True))
        # ACT #
        actual = sut.validate_pre_sds(value_usage, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION,
                      actual.status)

    def test_WHEN_referenced_value_in_symbol_table_has_valid_relativity_THEN_no_error(self):
        # ARRANGE #
        symbol_table = singleton_symbol_table(file_ref_entry('file_ref', file_refs.rel_home('home-file')))
        value_usage = vd.ValueReferenceOfPath('file_ref',
                                              PathRelativityVariants({RelOptionType.REL_ACT,
                                                                      RelOptionType.REL_HOME},
                                                                     False))
        # ACT #
        actual = sut.validate_pre_sds(value_usage, symbol_table)
        self.assertIsNone(actual, 'result should indicate success')

    def test_WHEN_referenced_value_is_in_symbol_table_THEN_None(self):
        # ARRANGE #
        symbol_table = singleton_symbol_table(value_definition_of('defined'))
        value_usage = vd.ValueReference('defined')
        # ACT #
        actual = sut.validate_pre_sds(value_usage, symbol_table)
        self.assertIsNone(actual)


class TestValueDefinition(unittest.TestCase):
    def test_WHEN_defined_value_is_in_symbol_table_THEN_validation_error(self):
        # ARRANGE #
        symbol_table = singleton_symbol_table(value_definition_of('already-defined'))
        value_usage = vd.ValueDefinition('already-defined')
        # ACT #
        actual = sut.validate_pre_sds(value_usage, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION,
                      actual.status)

    def test_WHEN_defined_value_not_in_symbol_table_THEN_None_and_added_to_symbol_table(self):
        # ARRANGE #
        symbol_table = singleton_symbol_table(value_definition_of('other'))
        value_usage = vd.ValueDefinition('undefined')
        # ACT #
        actual = sut.validate_pre_sds(value_usage, symbol_table)
        self.assertIsNone(actual, 'return value for indicating')
        self.assertTrue(symbol_table.contains('undefined'),
                        'definition should be added to symbol table')
        self.assertTrue(symbol_table.contains('other'),
                        'definition in symbol table before definition should remain there')

    def test_WHEN_defined_value_not_in_symbol_table_but_referenced_values_not_in_table_THEN_validation_error(self):
        # ARRANGE #
        symbol_table = singleton_symbol_table(value_definition_of('OTHER'))
        value_usage = vd.ValueDefinitionOfPath(
            'UNDEFINED',
            file_ref_value(
                file_refs.rel_value_definition(
                    vd.ValueReferenceOfPath(
                        'REFERENCED',
                        _path_relativity_variants_with_accepted(RelOptionType.REL_HOME)),
                    'file-name')))
        # ACT #
        actual = sut.validate_pre_sds(value_usage, symbol_table)
        self.assertIsNotNone(actual, 'return value for indicating error')

    def test_WHEN_defined_value_not_in_table_but_referenced_value_in_table_with_invalid_relativity_THEN_error(
            self):
        # ARRANGE #
        referenced_definition = vd.ValueDefinitionOfPath('REFERENCED',
                                                         file_ref_value(file_refs.rel_act('file-rel-act')))
        symbol_table = singleton_symbol_table(referenced_definition.symbol_table_entry)
        value_usage_to_check = vd.ValueDefinitionOfPath(
            'UNDEFINED',
            file_ref_value(
                file_refs.rel_value_definition(
                    vd.ValueReferenceOfPath(
                        referenced_definition.name,
                        _path_relativity_variants_with_accepted(RelOptionType.REL_HOME)),
                    'file-name')))
        # ACT #
        actual = sut.validate_pre_sds(value_usage_to_check, symbol_table)
        # ASSERT #
        self.assertIsNotNone(actual, 'return value for indicating error')

    def test_WHEN_defined_value_not_in_symbol_table_and_referenced_value_is_in_table_with_valid_relativity_THEN_ok(
            self):
        # ARRANGE #
        referenced_definition = vd.ValueDefinitionOfPath('REFERENCED',
                                                         file_ref_value(file_refs.rel_home('file-rel-home')))
        symbol_table = singleton_symbol_table(referenced_definition.symbol_table_entry)
        value_usage_to_check = vd.ValueDefinitionOfPath(
            'UNDEFINED',
            file_ref_value(
                file_refs.rel_value_definition(
                    vd.ValueReferenceOfPath(referenced_definition.name,
                                            _path_relativity_variants_with_accepted(RelOptionType.REL_HOME)),
                    'file-name')))
        # ACT #
        actual = sut.validate_pre_sds(value_usage_to_check, symbol_table)
        # ASSERT #
        self.assertIsNone(actual, 'return value for indicating success')
        self.assertTrue(symbol_table.contains('UNDEFINED'),
                        'definition should have been added')


def value_definition_of(name: str) -> Entry:
    return vd.ValueDefinition(name).symbol_table_entry


def file_ref_entry(name: str, file_ref: FileRef) -> Entry:
    return vd.ValueDefinitionOfPath(name, file_ref_value(file_ref)).symbol_table_entry


def _path_relativity_variants_with_accepted(accepted: RelOptionType) -> PathRelativityVariants:
    return PathRelativityVariants({accepted}, False)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
