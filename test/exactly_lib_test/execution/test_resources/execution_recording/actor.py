from typing import Sequence

from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.test_case.phases.act.actor import Actor, ActionToCheck
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
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
        self._recorder = recorder
        self._wrapped = wrapped
        self._parse_action = parse_action

    def parse(self, instructions: Sequence[ActPhaseInstruction]) -> ActionToCheck:
        self._recorder.recording_of(phase_step.ACT__PARSE).record()
        self._parse_action(instructions)

        return ActionToCheckWrapperThatRecordsSteps(self._recorder,
                                                    self._wrapped.parse(instructions))


def actor_of_constant(recorder: ListRecorder,
                      wrapped: ActionToCheck,
                      parse_action=actions.do_nothing,
                      ) -> Actor:
    return ActorThatRecordsSteps(
        recorder,
        ActorForConstantAtc(wrapped),
        parse_action=parse_action,
    )
