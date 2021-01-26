from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.execution.partial_execution.setup_settings_handler import StandardSetupSettingsHandler
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.test_case.phases.act.adv_w_validation import AdvWValidation
from exactly_lib.test_case.phases.act.execution_input import ActExecutionInput
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.type_val_deps.dep_variants.adv_w_validation.impls import ValidatorFunction
from exactly_lib_test.execution.test_resources.execution_recording.recorder import ListRecorder


class SetupSettingsHandlerThatRecordsValidation(StandardSetupSettingsHandler):
    def __init__(self,
                 recorder: ListRecorder,
                 custom_act_execution_input_validator: Optional[ValidatorFunction] = None,
                 ):
        super().__init__(SetupSettingsBuilder.new_empty())
        self._recorder = recorder
        self._custom_act_execution_input_validator = custom_act_execution_input_validator

    def as_act_execution_input(self) -> AdvWValidation[ActExecutionInput]:
        return _AdvThatRecordsValidation(
            self._recorder,
            super().as_act_execution_input(),
            self._custom_act_execution_input_validator,
        )


class _AdvThatRecordsValidation(AdvWValidation[ActExecutionInput]):
    def __init__(self,
                 recorder: ListRecorder,
                 wrapped: AdvWValidation[ActExecutionInput],
                 custom_act_execution_input_validator: Optional[ValidatorFunction],
                 ):
        self._recorder = recorder
        self._wrapped = wrapped
        self._custom_act_execution_input_validator = custom_act_execution_input_validator

    def validate(self) -> Optional[TextRenderer]:
        self._recorder.recording_of(phase_step.ACT__VALIDATE_EXE_INPUT).record()

        if self._custom_act_execution_input_validator is not None:
            return self._custom_act_execution_input_validator()
        else:
            return self._wrapped.validate()

    def resolve(self, environment: ApplicationEnvironment) -> ActExecutionInput:
        return self._wrapped.resolve(environment)
