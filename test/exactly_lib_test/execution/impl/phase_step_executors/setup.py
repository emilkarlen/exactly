import unittest
from typing import List, Set

from exactly_lib.execution.impl.single_instruction_executor import PartialControlledFailureEnum, \
    PartialInstructionControlledFailureInfo
from exactly_lib.execution.partial_execution.impl.symbol_validation import ValidateSymbolsExecutor
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that
from exactly_lib_test.symbol.test_resources.string import StringConstantSymbolContext, StringSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_hds
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return _suite_for(PhaseConfiguration())


class PhaseConfiguration:
    def instruction_with_usage(self, symbol_usages: list) -> SetupPhaseInstruction:
        return setup_phase_instruction_that(symbol_usages=do_return(symbol_usages))


def _suite_for(phase_configuration: PhaseConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        TestSymbolReference(phase_configuration),
        TestValueDefinition(phase_configuration),
        TestCombinationOfDefinitionAndReference(phase_configuration),
    ])


class TestSymbolReference(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, phase_configuration: PhaseConfiguration):
        super().__init__(phase_configuration)
        self.phase_configuration = phase_configuration

    def runTest(self):
        symbol__defined = symbol_of('defined')
        symbol__defined1 = symbol_of('defined1')
        symbol__defined2 = symbol_of('defined2')
        symbol__undefined = symbol_of('undefined')
        test_cases = [
            ('WHEN referenced value not in symbol table THEN error',
             Arrangement(symbol_usages=[symbol__undefined.reference__any_data_type],
                         environment=env_with_empty_symbol_table()),
             Expectation(return_value=error_with_status(PartialControlledFailureEnum.VALIDATION_ERROR),
                         environment=symbol_table_is_empty())
             ),
            ('WHEN referenced value is in symbol table THEN None',
             Arrangement(symbol_usages=[symbol__defined.reference__any_data_type],
                         environment=env_with_singleton_symbol_table(symbol__defined)),
             Expectation(return_value=is_success,
                         environment=symbol_table_contains_exactly_names({symbol__defined.name}))
             ),
            ('WHEN referenced valueS is in symbol table THEN None',
             Arrangement(symbol_usages=[symbol__defined1.reference__any_data_type,
                                        symbol__defined2.reference__any_data_type],
                         environment=env_with_symbol_table([symbol__defined1,
                                                            symbol__defined2])),
             Expectation(return_value=is_success,
                         environment=symbol_table_contains_exactly_names(
                             {symbol__defined1.name, symbol__defined2.name}))
             ),
            ('WHEN at least one referenced value is not in symbol table THEN error',
             Arrangement(symbol_usages=[symbol__defined.reference__any_data_type,
                                        symbol__undefined.reference__any_data_type],
                         environment=env_with_symbol_table([symbol__defined])),
             Expectation(return_value=error_with_status(PartialControlledFailureEnum.VALIDATION_ERROR),
                         environment=symbol_table_contains_exactly_names({symbol__defined.name}))
             ),
        ]
        for test_name, arrangement, expectation in test_cases:
            with self.subTest(msg=test_name):
                _check(self, self.phase_configuration, arrangement, expectation)


class TestValueDefinition(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, phase_configuration: PhaseConfiguration):
        super().__init__(phase_configuration)
        self.phase_configuration = phase_configuration

    def runTest(self):
        test_cases = [
            ('WHEN value to defined is in symbol table THEN validation error',
             Arrangement(symbol_usages=[StringConstantSymbolContext('already-defined').definition],
                         environment=env_with_singleton_symbol_table(symbol_of('already-defined'))),
             Expectation(return_value=error_with_status(PartialControlledFailureEnum.VALIDATION_ERROR),
                         environment=symbol_table_contains_exactly_names({'already-defined'}))
             ),
            ('WHEN defined value not in symbol table THEN None and added to symbol table',
             Arrangement(symbol_usages=[StringConstantSymbolContext('undefined').definition],
                         environment=env_with_singleton_symbol_table(symbol_of('other'))),
             Expectation(return_value=is_success,
                         environment=symbol_table_contains_exactly_names({'undefined', 'other'}))
             ),
            ('WHEN defined valueS not in symbol table THEN None and added to symbol table',
             Arrangement(symbol_usages=[StringConstantSymbolContext('undefined1').definition,
                                        StringConstantSymbolContext('undefined2').definition],
                         environment=env_with_singleton_symbol_table(symbol_of('other'))),
             Expectation(return_value=is_success,
                         environment=symbol_table_contains_exactly_names({'undefined1', 'undefined2', 'other'}))
             ),
            ('WHEN at least one value to define is in symbol table THEN validation error',
             Arrangement(symbol_usages=[StringConstantSymbolContext('undefined').definition,
                                        StringConstantSymbolContext('already-defined').definition],
                         environment=env_with_singleton_symbol_table(symbol_of('already-defined'))),
             Expectation(return_value=error_with_status(PartialControlledFailureEnum.VALIDATION_ERROR),
                         environment=symbol_table_contains_exactly_names({'undefined', 'already-defined'}))
             ),
        ]
        for test_name, arrangement, expectation in test_cases:
            with self.subTest(msg=test_name):
                _check(self, self.phase_configuration, arrangement, expectation)


class TestCombinationOfDefinitionAndReference(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, phase_configuration: PhaseConfiguration):
        super().__init__(phase_configuration)
        self.phase_configuration = phase_configuration

    def runTest(self):
        string_symbol = StringConstantSymbolContext('define')
        test_cases = [
            ('WHEN value to define is before reference to it (in list of value usages) THEN ok',
             Arrangement(symbol_usages=[string_symbol.definition,
                                        string_symbol.reference__any_data_type],
                         environment=env_with_empty_symbol_table()),
             Expectation(return_value=is_success,
                         environment=symbol_table_contains_exactly_names({'define'}))
             ),
            ('WHEN value to define is after reference to it (in list of value usages) THEN error',
             Arrangement(symbol_usages=[string_symbol.reference__any_data_type,
                                        string_symbol.definition],
                         environment=env_with_empty_symbol_table()),
             Expectation(return_value=error_with_status(PartialControlledFailureEnum.VALIDATION_ERROR),
                         environment=symbol_table_is_empty())
             ),
        ]
        for test_name, arrangement, expectation in test_cases:
            with self.subTest(msg=test_name):
                _check(self, self.phase_configuration, arrangement, expectation)


class Arrangement:
    def __init__(self,
                 symbol_usages: list,
                 environment: InstructionEnvironmentForPreSdsStep):
        self.symbol_usages = symbol_usages
        self.environment = environment


class Expectation:
    def __init__(self,
                 return_value: ValueAssertion = asrt.anything_goes(),
                 environment: ValueAssertion = asrt.anything_goes(),
                 ):
        self.return_value = return_value
        self.environment = environment


def env_with_empty_symbol_table() -> InstructionEnvironmentForPreSdsStep:
    hds = fake_hds()
    return InstructionEnvironmentForPreSdsStep(hds, ProcessExecutionSettings.with_empty_environ())


def env_with_singleton_symbol_table(symbol: SymbolContext) -> InstructionEnvironmentForPreSdsStep:
    table = symbol.symbol_table
    hds = fake_hds()
    return InstructionEnvironmentForPreSdsStep(hds,
                                               ProcessExecutionSettings.with_empty_environ(),
                                               symbols=table)


def env_with_symbol_table(symbols: List[SymbolContext]) -> InstructionEnvironmentForPreSdsStep:
    symbols = SymbolContext.symbol_table_of_contexts(symbols)
    hds = fake_hds()
    return InstructionEnvironmentForPreSdsStep(hds,
                                               ProcessExecutionSettings.with_empty_environ(),
                                               symbols=symbols)


def symbol_of(name: str) -> StringSymbolContext:
    return StringConstantSymbolContext(name)


def error_with_status(expected: PartialControlledFailureEnum) -> ValueAssertion:
    return asrt.is_not_none_and_instance_with(PartialInstructionControlledFailureInfo,
                                              asrt.sub_component('status',
                                                                 PartialInstructionControlledFailureInfo.status.fget,
                                                                 asrt.equals(expected)))


is_success = asrt.is_none


def symbol_table_contains_exactly_names(names: Set[str]) -> ValueAssertion[InstructionEnvironmentForPreSdsStep]:
    return _symbol_table_names_set(asrt.equals(names))


def symbol_table_is_empty() -> ValueAssertion[InstructionEnvironmentForPreSdsStep]:
    return _symbol_table_names_set(asrt.len_equals(0))


def _symbol_table_names_set(assertion: ValueAssertion[Set[str]]) -> ValueAssertion[InstructionEnvironmentForPreSdsStep]:
    return asrt.sub_component('symbols',
                              InstructionEnvironmentForPreSdsStep.symbols.fget,
                              asrt.sub_component('names_set',
                                                 SymbolTable.names_set.fget,
                                                 assertion))


def _check(put: unittest.TestCase,
           phase_configuration: PhaseConfiguration,
           arrangement: Arrangement,
           expectation: Expectation):
    # ARRANGE
    instruction = phase_configuration.instruction_with_usage(arrangement.symbol_usages)
    environment = arrangement.environment
    executor = ValidateSymbolsExecutor(environment.symbols)
    # ACT #
    return_value = executor.apply(instruction)
    # ASSERT #
    expectation.return_value.apply_with_message(put, return_value, 'return_value')
    expectation.environment.apply_with_message(put, environment, 'environment')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
