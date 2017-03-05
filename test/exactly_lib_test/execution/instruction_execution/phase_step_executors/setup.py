import pathlib
import unittest

from exactly_lib.execution.instruction_execution.phase_step_executors import SetupValidatePreSdsExecutor
from exactly_lib.execution.instruction_execution.single_instruction_executor import PartialControlledFailureEnum, \
    PartialInstructionControlledFailureInfo
from exactly_lib.test_case.phases import value_definition as vd
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib.test_case.phases.value_definition import SymbolTable
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return _suite_for(PhaseConfiguration())


class PhaseConfiguration:
    def instruction_with_usage(self, value_usages: list) -> SetupPhaseInstruction:
        return setup_phase_instruction_that(value_usages=value_usages)


def _suite_for(phase_configuration: PhaseConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        TestValueReference(phase_configuration),
        TestValueDefinition(phase_configuration),
    ])


class TestValueReference(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, phase_configuration: PhaseConfiguration):
        super().__init__(phase_configuration)
        self.phase_configuration = phase_configuration

    def runTest(self):
        test_cases = [
            ('WHEN referenced value not in symbol table THEN validation error',
             Arrangement(value_usages=[vd.ValueReference('undefined')],
                         environment=env_with_empty_symbol_table()),
             Expectation(return_value=error_with_status(PartialControlledFailureEnum.VALIDATION),
                         environment=symbol_table_is_empty())
             ),
            ('WHEN referenced value is in symbol table THEN None',
             Arrangement(value_usages=[vd.ValueReference('defined')],
                         environment=env_with_singleton_symbol_table(value_definition_of('defined'))),
             Expectation(return_value=is_success,
                         environment=symbol_table_contains_exactly_names({'defined'}))
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
            ('WHEN defined value is in symbol table THEN validation error',
             Arrangement(value_usages=[vd.ValueDefinition('already-defined')],
                         environment=env_with_singleton_symbol_table(value_definition_of('already-defined'))),
             Expectation(return_value=error_with_status(PartialControlledFailureEnum.VALIDATION),
                         environment=symbol_table_contains_exactly_names({'already-defined'}))
             ),
            ('WHEN defined value not in symbol table THEN None and added to symbol table',
             Arrangement(value_usages=[vd.ValueDefinition('undefined')],
                         environment=env_with_singleton_symbol_table(value_definition_of('other'))),
             Expectation(return_value=is_success,
                         environment=symbol_table_contains_exactly_names({'undefined', 'other'}))
             ),
        ]
        for test_name, arrangement, expectation in test_cases:
            with self.subTest(msg=test_name):
                _check(self, self.phase_configuration, arrangement, expectation)


class Arrangement:
    def __init__(self,
                 value_usages: list,
                 environment: InstructionEnvironmentForPreSdsStep):
        self.value_usages = value_usages
        self.environment = environment


class Expectation:
    def __init__(self,
                 return_value: asrt.ValueAssertion = asrt.anything_goes(),
                 environment: asrt.ValueAssertion = asrt.anything_goes(),
                 ):
        self.return_value = return_value
        self.environment = environment


def env_with_empty_symbol_table() -> InstructionEnvironmentForPreSdsStep:
    return InstructionEnvironmentForPreSdsStep(pathlib.Path(), {})


def env_with_singleton_symbol_table(definition: vd.ValueDefinition) -> InstructionEnvironmentForPreSdsStep:
    return InstructionEnvironmentForPreSdsStep(pathlib.Path(),
                                               {},
                                               value_definitions=SymbolTable({definition.name: definition}))


def value_definition_of(name: str) -> vd.ValueDefinition:
    return vd.ValueDefinition(name)


def error_with_status(expected: PartialControlledFailureEnum) -> asrt.ValueAssertion:
    return asrt.is_not_none_and_instance_with(PartialInstructionControlledFailureInfo,
                                              asrt.sub_component('status',
                                                                 PartialInstructionControlledFailureInfo.status.fget,
                                                                 asrt.equals(expected)))


is_success = asrt.is_none


def symbol_table_contains_exactly_names(names: set) -> asrt.ValueAssertion:
    return _symbol_table_names_set(asrt.equals(names))


def symbol_table_is_empty() -> asrt.ValueAssertion:
    return _symbol_table_names_set(asrt.len_equals(0))


def _symbol_table_names_set(assertion: asrt.ValueAssertion) -> asrt.ValueAssertion:
    return asrt.sub_component('value_definitions',
                              InstructionEnvironmentForPreSdsStep.value_definitions.fget,
                              asrt.sub_component('names_set',
                                                 SymbolTable.names_set.fget,
                                                 assertion))


def _check(put: unittest.TestCase,
           phase_configuration: PhaseConfiguration,
           arrangement: Arrangement,
           expectation: Expectation):
    # ARRANGE
    instruction = phase_configuration.instruction_with_usage(arrangement.value_usages)
    environment = arrangement.environment
    executor = SetupValidatePreSdsExecutor(environment)
    # ACT #
    return_value = executor.apply(instruction)
    # ASSERT #
    expectation.return_value.apply_with_message(put, return_value, 'return_value')
    expectation.environment.apply_with_message(put, environment, 'environment')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
