import unittest

from exactly_lib.execution.instruction_execution import value_definition_validation as sut
from exactly_lib.execution.instruction_execution.single_instruction_executor import PartialControlledFailureEnum
from exactly_lib.test_case import value_definition as vd


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestValueReference),
        unittest.makeSuite(TestValueDefinition),
    ])


class TestValueReference(unittest.TestCase):
    def test_WHEN_referenced_value_not_in_symbol_table_THEN_validation_error(self):
        # ARRANGE #
        symbol_table = vd.empty_symbol_table()
        value_usage = vd.ValueReference('undefined')
        # ACT #
        actual = sut.validate_pre_sds(value_usage, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION,
                      actual.status)

    def test_WHEN_referenced_value_is_in_symbol_table_THEN_None(self):
        # ARRANGE #
        symbol_table = vd.singleton_symbol_table(value_definition_of('defined'))
        value_usage = vd.ValueReference('defined')
        # ACT #
        actual = sut.validate_pre_sds(value_usage, symbol_table)
        self.assertIsNone(actual)


class TestValueDefinition(unittest.TestCase):
    def test_WHEN_defined_value_is_in_symbol_table_THEN_validation_error(self):
        # ARRANGE #
        symbol_table = vd.singleton_symbol_table(value_definition_of('already-defined'))
        value_usage = vd.ValueDefinition('already-defined')
        # ACT #
        actual = sut.validate_pre_sds(value_usage, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION,
                      actual.status)

    def test_WHEN_defined_value_not_in_symbol_table_THEN_None_and_added_to_symbol_table(self):
        # ARRANGE #
        symbol_table = vd.singleton_symbol_table(value_definition_of('other'))
        value_usage = vd.ValueDefinition('undefined')
        # ACT #
        actual = sut.validate_pre_sds(value_usage, symbol_table)
        self.assertIsNone(actual, 'return value for indicating')
        self.assertTrue(symbol_table.contains('undefined'),
                        'definition should be added to symbol table')
        self.assertTrue(symbol_table.contains('other'),
                        'definition in symbol table before definition should remain there')


def value_definition_of(name: str) -> vd.ValueDefinition:
    return vd.ValueDefinition(name)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
