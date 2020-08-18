from exactly_lib.definitions.entity import concepts
from exactly_lib.execution import phase_step
from exactly_lib.execution.impl import phase_step_execution
from exactly_lib.execution.result import PhaseStepFailureException, ExecutionFailureStatus
from exactly_lib.section_document.model import SectionContents, ElementType
from exactly_lib.test_case.actor import Actor, ActionToCheck, ParseException
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.render import combinators
from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct.rendering import component_renderers as comp_rend, blocks, line_objects
from exactly_lib.util.simple_textstruct.structure import LineElement
from exactly_lib.util.str_ import str_constructor


class ActionToCheckParser:
    def __init__(self, actor: NameAndValue[Actor]):
        self._actor = actor

    def parse(self, act_phase: SectionContents) -> ActionToCheck:
        """
        :raises PhaseStepFailureException
        """
        failure_con = phase_step_execution.PhaseStepFailureResultConstructor(phase_step.ACT__PARSE)

        instructions = []
        for element in act_phase.elements:
            if element.element_type is ElementType.INSTRUCTION:
                instruction = element.instruction_info.instruction
                if not isinstance(instruction, ActPhaseInstruction):
                    msg = 'Instruction is not an instance of ' + str(ActPhaseInstruction)
                    raise PhaseStepFailureException(failure_con.implementation_error_msg(msg))
                instructions.append(instruction)
            else:
                msg = 'Act phase contains an element that is not an instruction: ' + str(element.element_type)
                raise PhaseStepFailureException(failure_con.implementation_error_msg(msg))

        actor = self._actor.value

        def parse_action() -> ActionToCheck:
            try:
                return actor.parse(instructions)
            except ParseException as ex:
                raise PhaseStepFailureException(failure_con.apply(
                    ExecutionFailureStatus.VALIDATION_ERROR,
                    FailureDetails.new_message(
                        blocks.PrependFirstMinorBlockOfFirstMajorBlockR(
                            self._actor_info_lines(),
                            ex.cause)
                    )
                )
                )

        return phase_step_execution.execute_action_and_catch_implementation_exception(parse_action, failure_con)

    def _actor_info_lines(self) -> SequenceRenderer[LineElement]:
        return combinators.SingletonSequenceR(
            comp_rend.LineElementR(line_objects.StringLineObject(
                str_constructor.FormatMap(
                    '{actor:/u} "{actor_name}":',
                    {
                        'actor': concepts.ACTOR_CONCEPT_INFO.name,
                        'actor_name': self._actor.name,
                    }
                )
            ))
        )
