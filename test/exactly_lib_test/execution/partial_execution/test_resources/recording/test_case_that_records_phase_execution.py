import unittest
from typing import Callable, Sequence, Optional

from exactly_lib.execution.partial_execution.result import PartialExeResult
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.phases.act.actor import Actor
from exactly_lib.test_case.phases.act.execution_input import ActExecutionInput
from exactly_lib.test_case.phases.setup.settings_handler import SetupSettingsHandler
from exactly_lib.test_case.result import sh, svh
from exactly_lib.type_val_deps.dep_variants.adv_w_validation import impls as adv_impls
from exactly_lib.type_val_deps.dep_variants.adv_w_validation.impls import ValidatorFunction
from exactly_lib_test.execution.partial_execution.test_resources.recording.settings_handler import \
    SetupSettingsHandlerThatRecordsValidation
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorForExecutionRecording
from exactly_lib_test.execution.partial_execution.test_resources.test_case_base import PartialExecutionTestCaseBase
from exactly_lib_test.execution.test_resources.execution_recording import actor as recording_actor
from exactly_lib_test.execution.test_resources.execution_recording.recorder import \
    ListRecorder
from exactly_lib_test.test_case.actor.test_resources.action_to_checks import \
    ActionToCheckThatRunsConstantActions
from exactly_lib_test.test_case.actor.test_resources.execute_methods import ExecuteFunctionEh
from exactly_lib_test.test_case.actor.test_resources.test_actions import \
    execute_action_that_returns_exit_code, \
    prepare_action_that_returns
from exactly_lib_test.test_resources.actions import do_nothing, do_return
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

_VALID_EMPTY_AEI = adv_impls.ConstantAdvWValidation(ActExecutionInput.empty(),
                                                    adv_impls.unconditionally_successful_validator)


class Arrangement(tuple):
    def __new__(cls,
                test_case_generator: TestCaseGeneratorForExecutionRecording,
                actor_parse=do_nothing,
                atc_validate_post_setup=do_return(svh.new_svh_success()),
                atc_prepare=prepare_action_that_returns(sh.new_sh_success()),
                atc_execute: ExecuteFunctionEh = execute_action_that_returns_exit_code(),
                atc_validate_pre_sds=do_return(svh.new_svh_success()),
                atc_symbol_usages: Callable[[], Sequence[SymbolUsage]] = do_return([])
                ):
        return tuple.__new__(cls, (test_case_generator,
                                   atc_validate_post_setup,
                                   atc_prepare,
                                   atc_execute,
                                   atc_validate_pre_sds,
                                   atc_symbol_usages,
                                   actor_parse))

    @property
    def test_case_generator(self) -> TestCaseGeneratorForExecutionRecording:
        return self[0]

    @property
    def atc_validate_post_setup(self) -> Callable:
        return self[1]

    @property
    def atc_validate_pre_sds(self) -> Callable:
        return self[4]

    @property
    def atc_prepare(self) -> Callable:
        return self[2]

    @property
    def atc_execute(self) -> ExecuteFunctionEh:
        return self[3]

    @property
    def atc_symbol_usages(self) -> Callable:
        return self[5]

    @property
    def actor_parse(self) -> Callable:
        return self[6]


class Expectation(tuple):
    def __new__(cls,
                result: ValueAssertion[PartialExeResult],
                step_recordings: list):
        return tuple.__new__(cls, (result,
                                   step_recordings))

    @property
    def result(self) -> ValueAssertion[PartialExeResult]:
        return self[0]

    @property
    def step_recordings(self) -> list:
        return self[1]


class _TestCaseThatRecordsExecution(PartialExecutionTestCaseBase):
    """
    Base class for tests on a test case that uses the Python 3 language in the apply phase.
    """

    def __init__(self,
                 put: unittest.TestCase,
                 test_case_generator: TestCaseGeneratorForExecutionRecording,
                 expectation: Expectation,
                 dbg_do_not_delete_dir_structure=False,
                 actor: Optional[Actor] = None,
                 custom_act_execution_input_validator: Optional[ValidatorFunction] = None,
                 recorder: Optional[ListRecorder] = None,
                 ):
        super().__init__(put,
                         dbg_do_not_delete_dir_structure,
                         actor)
        self._custom_act_execution_input_validator = custom_act_execution_input_validator
        self._test_case_generator = test_case_generator
        self.__expectation = expectation
        self.__recorder = recorder
        if self.__recorder is None:
            self.__recorder = test_case_generator.recorder

    def _test_case(self) -> test_case_doc.TestCase:
        return self._test_case_generator.test_case

    def _settings_handler(self) -> SetupSettingsHandler:
        return SetupSettingsHandlerThatRecordsValidation(
            self._test_case_generator.recorder,
            self._custom_act_execution_input_validator,
        )

    def _assertions(self):
        self.__expectation.result.apply_with_message(self.put,
                                                     self.partial_result,
                                                     'result')

        msg = 'Difference in the sequence of executed phases and steps'
        self.put.assertListEqual(self.__expectation.step_recordings,
                                 self.__recorder.recorded_elements,
                                 msg)


class TestCaseBase(unittest.TestCase):
    def _check(self,
               arrangement: Arrangement,
               expectation: Expectation,
               custom_act_execution_input_validator: Optional[ValidatorFunction] = None,
               dbg_do_not_delete_dir_structure=False):
        execute_test_case_with_recording(self,
                                         arrangement,
                                         expectation,
                                         custom_act_execution_input_validator,
                                         dbg_do_not_delete_dir_structure)


def execute_test_case_with_recording(put: unittest.TestCase,
                                     arrangement: Arrangement,
                                     expectation: Expectation,
                                     custom_act_execution_input_validator: Optional[ValidatorFunction] = None,
                                     dbg_do_not_delete_dir_structure=False):
    constant_actions_atc = ActionToCheckThatRunsConstantActions(
        symbol_usages_action=arrangement.atc_symbol_usages,
        validate_pre_sds_action=arrangement.atc_validate_pre_sds,
        validate_post_setup_action=arrangement.atc_validate_post_setup,
        prepare_action=arrangement.atc_prepare,
        execute_action=arrangement.atc_execute,
    )
    actor = recording_actor.actor_of_constant(
        arrangement.test_case_generator.recorder,
        constant_actions_atc,
        parse_action=arrangement.actor_parse,
    )
    test_case = _TestCaseThatRecordsExecution(put,
                                              arrangement.test_case_generator,
                                              expectation,
                                              dbg_do_not_delete_dir_structure,
                                              actor,
                                              custom_act_execution_input_validator,
                                              arrangement.test_case_generator.recorder)
    test_case.execute()
