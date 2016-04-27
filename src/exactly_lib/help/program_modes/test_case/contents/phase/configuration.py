from exactly_lib.execution import phases
from exactly_lib.execution.execution_mode import NAME_SKIP
from exactly_lib.help.concepts.configuration_parameters.configuration_parameter import \
    EXECUTION_MODE_CONFIGURATION_PARAMETER
from exactly_lib.help.program_modes.test_case.contents.phase.utils import \
    pwd_at_start_of_phase_for_configuration_phase, \
    env_vars_for_configuration_phase
from exactly_lib.help.program_modes.test_case.contents_structure import TestCasePhaseInstructionSet
from exactly_lib.help.program_modes.test_case.phase_help_contents_structures import \
    TestCasePhaseDocumentationForPhaseWithInstructions, PhaseSequenceInfo, ExecutionEnvironmentInfo
from exactly_lib.help.utils.description import Description
from exactly_lib.help.utils.formatting import SectionName
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure.structures import para, text


class ConfigurationPhaseDocumentation(TestCasePhaseDocumentationForPhaseWithInstructions):
    def __init__(self,
                 name: str,
                 instruction_set: TestCasePhaseInstructionSet):
        super().__init__(name, instruction_set)

    def purpose(self) -> Description:
        return Description(text('Configures the execution of remaining phases, '
                                'and how the outcome of {0} is interpreted.'
                                .format(SectionName(phases.ASSERT.section_name).syntax)),
                           [para('TODO rest of purpose of the %s phase' % self.name.syntax)])

    def sequence_info(self) -> PhaseSequenceInfo:
        return PhaseSequenceInfo([para('This is the first phase of a test case.')],
                                 normalize_and_parse(PHASE_SEQUENCE__SUCCEEDING))

    def is_mandatory(self) -> bool:
        return False

    def instruction_purpose_description(self) -> list:
        return [para('TODO purpose of an instruction in the %s phase.' % self.name.syntax)]

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        return ExecutionEnvironmentInfo(pwd_at_start_of_phase_for_configuration_phase(),
                                        env_vars_for_configuration_phase())


PHASE_SEQUENCE__SUCCEEDING = """\
If {execution_mode} is set to {SKIP}, then the remaining phases are not executed.
""".format(execution_mode=EXECUTION_MODE_CONFIGURATION_PARAMETER.name().singular,
           SKIP=NAME_SKIP)
