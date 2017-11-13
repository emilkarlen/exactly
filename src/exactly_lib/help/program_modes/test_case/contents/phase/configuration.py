from exactly_lib.help.entities.concepts.configuration_parameters.execution_mode import \
    EXECUTION_MODE_CONFIGURATION_PARAMETER
from exactly_lib.help.entities.concepts.plain_concepts.configuration_parameter import CONFIGURATION_PARAMETER_CONCEPT
from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet
from exactly_lib.help.program_modes.test_case.contents.phase.utils import \
    cwd_at_start_of_phase_for_configuration_phase, \
    env_vars_for_configuration_phase
from exactly_lib.help.program_modes.test_case.phase_help_contents_structures import \
    TestCasePhaseDocumentationForPhaseWithInstructions, PhaseSequenceInfo, ExecutionEnvironmentInfo
from exactly_lib.help_texts.cross_reference_id import TestCasePhaseInstructionCrossReference, \
    TestCasePhaseCrossReference
from exactly_lib.help_texts.entity import concepts
from exactly_lib.help_texts.names import formatting
from exactly_lib.help_texts.test_case.instructions.instruction_names import EXECUTION_MODE_INSTRUCTION_NAME
from exactly_lib.help_texts.test_case.phase_names import SETUP_PHASE_NAME
from exactly_lib.test_case.execution_mode import NAME_SKIP
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.textformat_parser import TextParser


class ConfigurationPhaseDocumentation(TestCasePhaseDocumentationForPhaseWithInstructions):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        super().__init__(name, instruction_set)

        self._parser = TextParser({
            'configuration_parameters': formatting.concept(concepts.CONFIGURATION_PARAMETER_CONCEPT_INFO.singular_name),
            'execution_mode': formatting.concept(concepts.EXECUTION_MODE_CONF_PARAM_INFO.singular_name),
            'SKIP': NAME_SKIP,
            'setup': SETUP_PHASE_NAME,
        })

    def purpose(self) -> Description:
        first_line = self._parser.text(ONE_LINE_DESCRIPTION)
        remaining_lines = []
        return Description(first_line, remaining_lines)

    def sequence_info(self) -> PhaseSequenceInfo:
        preceding_phase = self._parser.fnap(SEQUENCE_INFO__PRECEDING_PHASE)
        succeeding_phase = self._parser.fnap(SEQUENCE_INFO__SUCCEEDING_PHASE)
        return PhaseSequenceInfo(preceding_phase, succeeding_phase)

    def is_mandatory(self) -> bool:
        return False

    def instruction_purpose_description(self) -> list:
        return self._parser.fnap(INSTRUCTION_PURPOSE_DESCRIPTION)

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        return ExecutionEnvironmentInfo(cwd_at_start_of_phase_for_configuration_phase(),
                                        env_vars_for_configuration_phase())

    @property
    def see_also_targets(self) -> list:
        return [
            CONFIGURATION_PARAMETER_CONCEPT.cross_reference_target(),
            EXECUTION_MODE_CONFIGURATION_PARAMETER.cross_reference_target(),
            TestCasePhaseInstructionCrossReference(self.name.plain,
                                                   EXECUTION_MODE_INSTRUCTION_NAME),
            TestCasePhaseCrossReference(SETUP_PHASE_NAME.plain),
        ]


ONE_LINE_DESCRIPTION = """\
Configures the execution of the remaining phases by setting {configuration_parameters}."""

INSTRUCTION_PURPOSE_DESCRIPTION = 'Each instruction sets one of the {configuration_parameters}.'

SEQUENCE_INFO__PRECEDING_PHASE = 'This is the first phase.'

SEQUENCE_INFO__SUCCEEDING_PHASE = """\
If the {execution_mode} is set to {SKIP}, then the remaining phases are not executed.

Otherwise, the {setup} phase follows.
"""
