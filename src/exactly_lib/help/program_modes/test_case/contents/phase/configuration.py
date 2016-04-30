from exactly_lib.default.program_modes.test_case.default_instruction_names import EXECUTION_MODE_INSTRUCTION_NAME
from exactly_lib.execution.execution_mode import NAME_SKIP
from exactly_lib.help.concepts.configuration_parameters.execution_mode import EXECUTION_MODE_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.plain_concepts.configuration_parameter import CONFIGURATION_PARAMETER_CONCEPT
from exactly_lib.help.cross_reference_id import TestCasePhaseInstructionCrossReference, TestCasePhaseCrossReference
from exactly_lib.help.program_modes.test_case.contents.phase.utils import \
    pwd_at_start_of_phase_for_configuration_phase, \
    env_vars_for_configuration_phase
from exactly_lib.help.program_modes.test_case.contents_structure import TestCasePhaseInstructionSet
from exactly_lib.help.program_modes.test_case.phase_help_contents_structures import \
    TestCasePhaseDocumentationForPhaseWithInstructions, PhaseSequenceInfo, ExecutionEnvironmentInfo
from exactly_lib.help.utils.description import Description
from exactly_lib.help.utils.phase_names import SETUP_PHASE_NAME
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs


class ConfigurationPhaseDocumentation(TestCasePhaseDocumentationForPhaseWithInstructions):
    def __init__(self,
                 name: str,
                 instruction_set: TestCasePhaseInstructionSet):
        super().__init__(name, instruction_set)

    def purpose(self) -> Description:
        first_line = docs.text(
            ONE_LINE_DESCRIPTION.format(configuration_parameters=CONFIGURATION_PARAMETER_CONCEPT.name().plural))
        remaining_lines = []
        return Description(first_line, remaining_lines)

    def sequence_info(self) -> PhaseSequenceInfo:
        preceding_phase = normalize_and_parse(SEQUENCE_INFO__PRECEDING_PHASE)
        succeeding_phase = normalize_and_parse(
            SEQUENCE_INFO__SUCCEEDING_PHASE.format(
                execution_mode=EXECUTION_MODE_CONFIGURATION_PARAMETER.name().singular,
                SKIP=NAME_SKIP,
                setup=SETUP_PHASE_NAME))
        return PhaseSequenceInfo(preceding_phase, succeeding_phase)

    def is_mandatory(self) -> bool:
        return False

    def instruction_purpose_description(self) -> list:
        return [docs.para(INSTRUCTION_PURPOSE_DESCRIPTION
                          .format(configuration_parameters=CONFIGURATION_PARAMETER_CONCEPT.name().plural))
                ]

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        return ExecutionEnvironmentInfo(pwd_at_start_of_phase_for_configuration_phase(),
                                        env_vars_for_configuration_phase())

    @property
    def see_also(self) -> list:
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
