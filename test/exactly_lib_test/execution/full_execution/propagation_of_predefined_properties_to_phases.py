import pathlib
import unittest

from exactly_lib.execution.configuration import PredefinedProperties
from exactly_lib.execution.phase_step_simple import \
    ALL_SETUP_WITH_ENV_ARG, ALL_ASSERT_WITH_ENV_ARG, ALL_BEFORE_ASSERT_WITH_ENV_ARG, \
    ALL_CLEANUP_WITH_ENV_ARG, ALL_ACT_WITH_ENV_ARG
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.util.functional import Composition
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.execution.full_execution.test_resources import execution_check, \
    result_assertions as asrt_full_result
from exactly_lib_test.execution.test_resources.execution_recording.recording2 import PropertyRecorderBuilder, \
    actor_that_records_property_of_env_for_each_step_w_env_arg, \
    test_case_that_records_property_of_env_for_each_step_of_partial_execution
from exactly_lib_test.symbol.test_resources.string import StringSymbolContext
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_keys_equals


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestPredefinedSymbols)


class TestPredefinedSymbols(unittest.TestCase):
    def test_WHEN_no_predefined_symbols_are_specified_THEN_the_set_of_symbols_SHOULD_be_empty(
            self):
        # ARRANGE #
        predefined_properties = PredefinedProperties(environ={},
                                                     predefined_symbols=None)
        self._check(predefined_properties, assert_symbol_table_keys_equals({}))

    def test_WHEN_predefined_symbols_are_specified_THEN_the_set_of_symbols_SHOULD_be_exactly_these_symbols(
            self):
        # ARRANGE #
        predefined_symbols_table = StringSymbolContext.of_constant(
            'predefined symbol',
            'predefined string value (not used by this test)').symbol_table
        predefined_properties = PredefinedProperties(environ={},
                                                     predefined_symbols=predefined_symbols_table)
        self._check(predefined_properties, assert_symbol_table_keys_equals(predefined_symbols_table.names_set))

    def _check(self,
               predefined_properties: PredefinedProperties,
               assertion_on_recorded_symbol_table: ValueAssertion):
        # ARRANGE #
        actual_recorded_steps = {}
        recorder_builder = PropertyRecorderBuilder(
            Composition(SymbolTable.copy,
                        InstructionEnvironmentForPreSdsStep.symbols.fget),
            actual_recorded_steps)
        test_case = test_case_that_records_property_of_env_for_each_step_of_partial_execution(recorder_builder)
        actor = actor_that_records_property_of_env_for_each_step_w_env_arg(recorder_builder)
        default_hds_dir = pathlib.Path.cwd()
        configuration_builder = ConfigurationBuilder(default_hds_dir,
                                                     default_hds_dir,
                                                     actor)
        arrangement = execution_check.Arrangement(test_case,
                                                  configuration_builder,
                                                  predefined_properties=predefined_properties)
        expectation = execution_check.Expectation(full_result=asrt_full_result.is_pass())
        # ACT & ASSERT #
        execution_check.check(self, arrangement, expectation)
        # ASSERT #
        expected_recorded_steps = frozenset(ALL_SETUP_WITH_ENV_ARG +
                                            ALL_ACT_WITH_ENV_ARG +
                                            ALL_BEFORE_ASSERT_WITH_ENV_ARG +
                                            ALL_ASSERT_WITH_ENV_ARG +
                                            ALL_CLEANUP_WITH_ENV_ARG)
        for expected_recorded_step in sorted(expected_recorded_steps,
                                             key=lambda simple_phase_step: (
                                                     simple_phase_step.phase.value, simple_phase_step.step)):
            self.assertIn(expected_recorded_step,
                          actual_recorded_steps,
                          'There should be a recording for the step')
            actual_recorded_symbol_table = actual_recorded_steps[expected_recorded_step]
            self.assertIsInstance(actual_recorded_symbol_table,
                                  SymbolTable,
                                  'It it is not a SymbolTable, then this test has an impl error')
            assertion_on_recorded_symbol_table.apply_with_message(self,
                                                                  actual_recorded_symbol_table,
                                                                  'Recording for step ' + str(expected_recorded_step))
        for actual_recorded_step in actual_recorded_steps.keys():
            self.assertIn(actual_recorded_step,
                          expected_recorded_steps,
                          'each actual step must be expected')
