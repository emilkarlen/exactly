from typing import Sequence

from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.test_case.actor import Actor, ActionToCheck
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib_test.execution.test_resources.execution_recording.action_to_check import \
    ActionToCheckWrapperThatRecordsSteps
from exactly_lib_test.execution.test_resources.execution_recording.recorder import ListRecorder
from exactly_lib_test.test_case.actor.test_resources.actor_impls import ActorForConstantAtc
from exactly_lib_test.test_resources import actions


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
