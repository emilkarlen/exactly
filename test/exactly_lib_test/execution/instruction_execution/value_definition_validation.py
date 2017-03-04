import unittest

from exactly_lib.execution.instruction_execution import value_definition_validation as sut
from exactly_lib.execution.instruction_execution.single_instruction_executor import PartialControlledFailureEnum
from exactly_lib.test_case.phases import value_definition


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestValueReference),
        unittest.makeSuite(TestValueDefinition),
    ])


class TestValueReference(unittest.TestCase):
    def test_when_referenced_value_does_not_exist_then_validation_error(self):
        # ARRANGE #
        symbol_table = value_definition.empty_symbol_table()
        value_usage = value_definition.ValueReference('undefined')
        # ACT #
        actual = sut.validate_pre_sds(value_usage, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION,
                      actual.status)

    def test_when_referenced_value_does_exist_then_None(self):
        # ARRANGE #
        symbol_table = value_definition.singleton_symbol_table('defined')
        value_usage = value_definition.ValueReference('defined')
        # ACT #
        actual = sut.validate_pre_sds(value_usage, symbol_table)
        self.assertIsNone(actual)


class TestValueDefinition(unittest.TestCase):
    def test_when_defined_value_already_defined_then_validation_error(self):
        # ARRANGE #
        symbol_table = value_definition.singleton_symbol_table('already-defined')
        value_usage = value_definition.ValueDefinition('already-defined')
        # ACT #
        actual = sut.validate_pre_sds(value_usage, symbol_table)
        self.assertIsNotNone(actual, 'result should indicate error')
        self.assertIs(PartialControlledFailureEnum.VALIDATION,
                      actual.status)

    def test_when_defined_value_not_already_defined_then_None_and_added_to_symbol_table(self):
        # ARRANGE #
        symbol_table = value_definition.singleton_symbol_table('other')
        value_usage = value_definition.ValueDefinition('undefined')
        # ACT #
        actual = sut.validate_pre_sds(value_usage, symbol_table)
        self.assertIsNone(actual, 'return value for indicating')
        self.assertIn('undefined', symbol_table,
                      'definition should be added to symbol table')
        self.assertIn('other', symbol_table,
                      'definition in symbol table before definition should remain there')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
