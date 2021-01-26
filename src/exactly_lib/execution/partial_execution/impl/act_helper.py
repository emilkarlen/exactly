from typing import List

from exactly_lib.execution import phase_step
from exactly_lib.execution.impl import phase_step_execution
from exactly_lib.execution.impl.phase_step_execution import PhaseStepFailureResultConstructor
from exactly_lib.execution.phase_step import PhaseStep
from exactly_lib.execution.result import PhaseStepFailureException, ExecutionFailureStatus
from exactly_lib.impls.actors.util import source_code_lines
from exactly_lib.section_document.model import SectionContents, ElementType
from exactly_lib.test_case.phases.act.actor import Actor, ActionToCheck, ParseException
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.util.str_ import misc_formatting


class ActHelper:
    def __init__(self,
                 actor_name: str,
                 act_phase: SectionContents,
                 ):
        self._actor_name = actor_name
        self.act_phase = act_phase
        self.instructions = self._instructions_in(act_phase)
        self.act_source_str = misc_formatting.lines_content(
            source_code_lines.all_source_code_lines(self.instructions)
        )

    def failure_constructor(self, step: PhaseStep) -> PhaseStepFailureResultConstructor:
        return PhaseStepFailureResultConstructor(step,
                                                 self._actor_name,
                                                 self.act_source_str)

    def parse(self, actor: Actor) -> ActionToCheck:
        failure_constructor = self.failure_constructor(phase_step.ACT__PARSE)

        def parse_action() -> ActionToCheck:
            try:
                return actor.parse(self.instructions)
            except ParseException as ex:
                raise PhaseStepFailureException(
                    failure_constructor.apply(
                        ExecutionFailureStatus.SYNTAX_ERROR,
                        FailureDetails.new_message(ex.cause)
                    )
                )

        return phase_step_execution.execute_action_and_catch_internal_error_exception(parse_action,
                                                                                      failure_constructor)

    @staticmethod
    def _instructions_in(act_phase: SectionContents,
                         ) -> List[ActPhaseInstruction]:
        ret_val = []
        for element in act_phase.elements:
            if element.element_type is ElementType.INSTRUCTION:
                instruction = element.instruction_info.instruction
                assert isinstance(instruction, ActPhaseInstruction)
                ret_val.append(instruction)

        return ret_val
