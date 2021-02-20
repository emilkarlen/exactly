from typing import List

from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.test_case import phase_names, phase_infos
from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet
from exactly_lib.help.program_modes.test_case.contents.phase.utils import \
    cwd_at_start_of_phase_first_phase_executed_in_the_sandbox, sequence_info__succeeding_phase, \
    sequence_info__not_executed_if_execution_mode_is_skip
from exactly_lib.help.program_modes.test_case.contents_structure.phase_documentation import \
    TestCasePhaseDocumentationForPhaseWithInstructions, PhaseSequenceInfo, ExecutionEnvironmentInfo
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class SetupPhaseDocumentation(TestCasePhaseDocumentationForPhaseWithInstructions):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        super().__init__(name, instruction_set)
        self._tp = TextParser({
            'phase': phase_names.PHASE_NAME_DICTIONARY,
            'ATC': formatting.concept_(concepts.ACTION_TO_CHECK_CONCEPT_INFO),
            'env_var': concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.name,
            'env_vars_default': concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.default,
            'timeout_default': concepts.TIMEOUT_CONCEPT_INFO.default,
            'stdin': misc_texts.STDIN,
            'SDS': concepts.SDS_CONCEPT_INFO.name,
        })

    def purpose(self) -> Description:
        return Description(self._tp.text(ONE_LINE_DESCRIPTION),
                           self._tp.fnap(REST_OF_DESCRIPTION))

    def sequence_info(self) -> PhaseSequenceInfo:
        return PhaseSequenceInfo(self._tp.fnap(SEQUENCE_INFO__PRECEDING_PHASE),
                                 sequence_info__succeeding_phase(phase_names.ACT),
                                 prelude=sequence_info__not_executed_if_execution_mode_is_skip())

    def instruction_purpose_description(self) -> List[ParagraphItem]:
        return self._tp.fnap(INSTRUCTION_PURPOSE_DESCRIPTION)

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        return ExecutionEnvironmentInfo(cwd_at_start_of_phase_first_phase_executed_in_the_sandbox(),
                                        environment_variables_prologue=self._tp.fnap(ENV_VARS_PROLOGUE),
                                        timeout_prologue=self._tp.fnap(TIMEOUT_PROLOGUE))

    @property
    def _see_also_targets_specific(self) -> List[SeeAlsoTarget]:
        return [
            concepts.SDS_CONCEPT_INFO.cross_reference_target,
            concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO.cross_reference_target,
            concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.cross_reference_target,
            concepts.TIMEOUT_CONCEPT_INFO.cross_reference_target,
            phase_infos.CONFIGURATION.cross_reference_target,
            phase_infos.ACT.cross_reference_target,
        ]


ONE_LINE_DESCRIPTION = """\
Sets up the environment that the {ATC}
(the {phase[act]} phase) is executed in.
"""

REST_OF_DESCRIPTION = """\
E.g.


 * populating the {SDS:/q} with files and directories
 * setting the contents of {stdin}
 * setting {env_var:s}
 * setting up external resources, such as databases.
"""

INSTRUCTION_PURPOSE_DESCRIPTION = """\
Each instruction should probably have some side effect that affects
the {ATC}.
"""

SEQUENCE_INFO__PRECEDING_PHASE = """\
This phase follows the {phase[conf]} phase,
and is the first phase that is executed with the {SDS:/q}.
"""

ENV_VARS_PROLOGUE = """\
Default: {env_vars_default}.
"""

TIMEOUT_PROLOGUE = """\
Default: {timeout_default}.
"""
