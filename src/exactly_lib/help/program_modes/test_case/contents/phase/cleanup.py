from typing import List

from exactly_lib.definitions import formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import concepts, conf_params
from exactly_lib.definitions.test_case import phase_names, phase_infos
from exactly_lib.definitions.test_case.instructions.instruction_names import TEST_CASE_STATUS_INSTRUCTION_NAME
from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet
from exactly_lib.help.program_modes.test_case.contents.phase.utils import \
    cwd_at_start_of_phase_for_non_first_phases, sequence_info__not_executed_if_execution_mode_is_skip, \
    env_vars_prologue_for_inherited_from_previous_phase, timeout_prologue_for_inherited_from_previous_phase
from exactly_lib.help.program_modes.test_case.contents_structure.phase_documentation import \
    TestCasePhaseDocumentationForPhaseWithInstructions, PhaseSequenceInfo, ExecutionEnvironmentInfo
from exactly_lib.test_case.test_case_status import NAME_SKIP
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class CleanupPhaseDocumentation(TestCasePhaseDocumentationForPhaseWithInstructions):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        super().__init__(name, instruction_set)
        self._tp = TextParser({
            'phase': phase_names.PHASE_NAME_DICTIONARY,
            'SKIP': NAME_SKIP,
            'execution_mode': formatting.conf_param_(conf_params.TEST_CASE_STATUS_CONF_PARAM_INFO),
            'ATC': formatting.concept_(concepts.ACTION_TO_CHECK_CONCEPT_INFO),
        })

    def purpose(self) -> Description:
        return Description(self._tp.text(ONE_LINE_DESCRIPTION),
                           self._tp.fnap(REST_OF_DESCRIPTION))

    def sequence_info(self) -> PhaseSequenceInfo:
        return PhaseSequenceInfo(self._tp.fnap(_SEQUENCE_INFO__PRECEDING_PHASE),
                                 self._tp.fnap(_SEQUENCE_INFO__SUCCEEDING_PHASE),
                                 prelude=sequence_info__not_executed_if_execution_mode_is_skip())

    def instruction_purpose_description(self) -> List[ParagraphItem]:
        return self._tp.fnap(INSTRUCTION_PURPOSE_DESCRIPTION)

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        return ExecutionEnvironmentInfo(
            cwd_at_start_of_phase_for_non_first_phases(),
            environment_variables_prologue=env_vars_prologue_for_inherited_from_previous_phase(),
            timeout_prologue=timeout_prologue_for_inherited_from_previous_phase(),
        )

    @property
    def _see_also_targets_specific(self) -> List[SeeAlsoTarget]:
        return [
            concepts.SDS_CONCEPT_INFO.cross_reference_target,
            concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO.cross_reference_target,
            concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.cross_reference_target,
            concepts.TIMEOUT_CONCEPT_INFO.cross_reference_target,
            conf_params.TEST_CASE_STATUS_CONF_PARAM_INFO.cross_reference_target,
            phase_infos.ASSERT.cross_reference_target,
            phase_infos.CONFIGURATION.instruction_cross_reference_target(TEST_CASE_STATUS_INSTRUCTION_NAME),
        ]


ONE_LINE_DESCRIPTION = """\
Cleans up pollution from earlier phases that exist outside of the sandbox
(e.g. in a database).
"""

REST_OF_DESCRIPTION = """\
Pollution can come from an earlier phase such as {phase[setup]:syntax},
or the {ATC} of the {phase[act]} phase.
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
