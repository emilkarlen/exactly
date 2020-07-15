import pathlib
from typing import Sequence

from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.actor import ActionToCheck, Actor, AtcOsProcessExecutor
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import sh, svh
from exactly_lib.test_case.result.eh import ExitCodeOrHardError
from exactly_lib.util.file_utils.std import StdFiles
from exactly_lib_test.execution.test_resources.execution_recording.recorder import ListRecorder
from exactly_lib_test.test_case.actor.test_resources.actor_impls import \
    ActorForConstantAtc
from exactly_lib_test.test_resources import actions


class ActionToCheckWrapperThatRecordsSteps(ActionToCheck):
    def __init__(self,
                 recorder: ListRecorder,
                 wrapped: ActionToCheck):
        self.__recorder = recorder
        self.__wrapped = wrapped

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        self.__recorder.recording_of(phase_step.ACT__VALIDATE_SYMBOLS).record()
        return self.__wrapped.symbol_usages()

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder.recording_of(phase_step.ACT__VALIDATE_PRE_SDS).record()
        return self.__wrapped.validate_pre_sds(environment)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder.recording_of(phase_step.ACT__VALIDATE_POST_SETUP).record()
        return self.__wrapped.validate_post_setup(environment)

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_process_executor: AtcOsProcessExecutor,
                script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        self.__recorder.recording_of(phase_step.ACT__PREPARE).record()
        return self.__wrapped.prepare(environment, os_process_executor, script_output_dir_path)

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_process_executor: AtcOsProcessExecutor,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        self.__recorder.recording_of(phase_step.ACT__EXECUTE).record()
        return self.__wrapped.execute(environment, os_process_executor, script_output_dir_path, std_files)


class ActorThatRecordsSteps(Actor):
    def __init__(self,
                 recorder: ListRecorder,
                 wrapped: Actor,
                 parse_action=actions.do_nothing,
                 ):
        self.__recorder = recorder
        self.__wrapped = wrapped
        self.__parse_action = parse_action

    def parse(self, instructions: Sequence[ActPhaseInstruction]) -> ActionToCheck:
        self.__recorder.recording_of(phase_step.ACT__PARSE).record()
        self.__parse_action(instructions)

        return ActionToCheckWrapperThatRecordsSteps(self.__recorder,
                                                    self.__wrapped.parse(instructions))


def actor_of_constant(recorder: ListRecorder,
                      wrapped: ActionToCheck,
                      parse_action=actions.do_nothing,
                      ) -> Actor:
    return ActorThatRecordsSteps(
        recorder,
        ActorForConstantAtc(wrapped),
        parse_action=parse_action,
    )
