from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet
from exactly_lib.help.program_modes.test_case.contents.phase.utils import \
    cwd_at_start_of_phase_for_non_first_phases, sequence_info__not_executed_if_execution_mode_is_skip
from exactly_lib.help.program_modes.test_case.phase_help_contents_structures import \
    TestCasePhaseDocumentationForPhaseWithInstructions, PhaseSequenceInfo, ExecutionEnvironmentInfo
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.cross_ref.concrete_cross_refs import TestCasePhaseCrossReference, \
    TestCasePhaseInstructionCrossReference
from exactly_lib.help_texts.entity import concepts, conf_params
from exactly_lib.help_texts.test_case.instructions.instruction_names import TEST_CASE_STATUS_INSTRUCTION_NAME
from exactly_lib.help_texts.test_case.phase_names import ASSERT_PHASE_NAME, \
    CONFIGURATION_PHASE_NAME, PHASE_NAME_DICTIONARY
from exactly_lib.test_case.test_case_status import NAME_SKIP
from exactly_lib.test_case_file_structure.environment_variables import EXISTS_AT_BEFORE_ASSERT_MAIN
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.textformat_parser import TextParser


class CleanupPhaseDocumentation(TestCasePhaseDocumentationForPhaseWithInstructions):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        super().__init__(name, instruction_set)
        self._tp = TextParser({
            'phase': PHASE_NAME_DICTIONARY,
            'SKIP': NAME_SKIP,
            'execution_mode': formatting.conf_param_(conf_params.TEST_CASE_STATUS_CONF_PARAM_INFO),
        })

    def purpose(self) -> Description:
        return Description(self._tp.text(ONE_LINE_DESCRIPTION),
                           self._tp.fnap(REST_OF_DESCRIPTION))

    def sequence_info(self) -> PhaseSequenceInfo:
        return PhaseSequenceInfo(self._tp.fnap(_SEQUENCE_INFO__PRECEDING_PHASE),
                                 self._tp.fnap(_SEQUENCE_INFO__SUCCEEDING_PHASE),
                                 prelude=sequence_info__not_executed_if_execution_mode_is_skip())

    def is_mandatory(self) -> bool:
        return False

    def instruction_purpose_description(self) -> list:
        return self._tp.fnap(INSTRUCTION_PURPOSE_DESCRIPTION)

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        return ExecutionEnvironmentInfo(cwd_at_start_of_phase_for_non_first_phases(),
                                        EXISTS_AT_BEFORE_ASSERT_MAIN)

    @property
    def see_also_targets(self) -> list:
        return [
            concepts.SANDBOX_CONCEPT_INFO.cross_reference_target,
            concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.cross_reference_target,
            conf_params.TEST_CASE_STATUS_CONF_PARAM_INFO.cross_reference_target,
            TestCasePhaseCrossReference(ASSERT_PHASE_NAME.plain),
            TestCasePhaseInstructionCrossReference(CONFIGURATION_PHASE_NAME.plain,
                                                   TEST_CASE_STATUS_INSTRUCTION_NAME),
        ]


ONE_LINE_DESCRIPTION = """\
Cleans up pollution from earlier phases that exist outside of the sandbox
(e.g. in a database).
"""

REST_OF_DESCRIPTION = """\
Pollution can come from an earlier phase such as {phase[setup]:syntax},
or the system under test (SUT) of the {phase[act]} phase.
"""

INSTRUCTION_PURPOSE_DESCRIPTION = """\
Each instruction probably has some side effect that does some cleanup.
"""

_SEQUENCE_INFO__PRECEDING_PHASE = """\
This phase is always executed.


If an instruction in an earlier phase encountered an unexpected error,
then execution has jumped directly from that instruction to this phase.

If no unexpected error has occurred, then this phase follows the {phase[assert]} phase.
"""

_SEQUENCE_INFO__SUCCEEDING_PHASE = """\
This is the last phase.
"""
