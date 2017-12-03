from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet
from exactly_lib.help.program_modes.test_case.contents.phase.utils import \
    cwd_at_start_of_phase_first_phase_executed_in_the_sandbox, sequence_info__succeeding_phase, \
    sequence_info__not_executed_if_execution_mode_is_skip
from exactly_lib.help.program_modes.test_case.phase_help_contents_structures import \
    TestCasePhaseDocumentationForPhaseWithInstructions, PhaseSequenceInfo, ExecutionEnvironmentInfo
from exactly_lib.help_texts.cross_ref.concrete_cross_refs import TestCasePhaseCrossReference
from exactly_lib.help_texts.entity import concepts
from exactly_lib.help_texts.test_case.phase_names import ACT_PHASE_NAME, \
    CONFIGURATION_PHASE_NAME, PHASE_NAME_DICTIONARY
from exactly_lib.test_case_file_structure.environment_variables import EXISTS_AT_SETUP_MAIN
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.textformat_parser import TextParser


class SetupPhaseDocumentation(TestCasePhaseDocumentationForPhaseWithInstructions):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        super().__init__(name, instruction_set)
        self._tp = TextParser({
            'phase': PHASE_NAME_DICTIONARY
        })

    def purpose(self) -> Description:
        return Description(self._tp.text(ONE_LINE_DESCRIPTION),
                           self._tp.fnap(REST_OF_DESCRIPTION))

    def sequence_info(self) -> PhaseSequenceInfo:
        return PhaseSequenceInfo(self._tp.fnap(SEQUENCE_INFO__PRECEDING_PHASE),
                                 sequence_info__succeeding_phase(ACT_PHASE_NAME),
                                 prelude=sequence_info__not_executed_if_execution_mode_is_skip())

    def is_mandatory(self) -> bool:
        return False

    def instruction_purpose_description(self) -> list:
        return self._tp.fnap(INSTRUCTION_PURPOSE_DESCRIPTION)

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        return ExecutionEnvironmentInfo(cwd_at_start_of_phase_first_phase_executed_in_the_sandbox(),
                                        EXISTS_AT_SETUP_MAIN)

    @property
    def see_also_targets(self) -> list:
        return [
            concepts.SANDBOX_CONCEPT_INFO.cross_reference_target,
            concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.cross_reference_target,
            TestCasePhaseCrossReference(CONFIGURATION_PHASE_NAME.plain),
            TestCasePhaseCrossReference(ACT_PHASE_NAME.plain),
        ]


ONE_LINE_DESCRIPTION = """\
Sets up the environment that the system under test
(the {phase[act]} phase) will be executed in.
"""

REST_OF_DESCRIPTION = """\
E.g.


 * populating the current directory with files and directories
 * setting the contents of stdin
 * setting environment variables
 * setting up external resources, such as databases.
"""

INSTRUCTION_PURPOSE_DESCRIPTION = """\
Each instruction should probably have some side effect that affects
the system under test (the {phase[act]} phase).
"""

SEQUENCE_INFO__PRECEDING_PHASE = """\
This phase follows the {phase[conf]} phase,
and is the first phase that is executed in the sandbox.
"""
