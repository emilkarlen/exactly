from typing import List

from exactly_lib.definitions import formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.test_case import phase_names, phase_infos
from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet
from exactly_lib.help.program_modes.test_case.contents.phase.utils import \
    sequence_info__succeeding_phase, \
    sequence_info__preceding_phase, \
    sequence_info__not_executed_if_execution_mode_is_skip, execution_environment_prologue_for_post_act_phase, \
    cwd_at_start_of_phase_is_same_as_at_end_of_the, env_vars_prologue_for_inherited_from_previous_phase
from exactly_lib.help.program_modes.test_case.contents_structure.phase_documentation import \
    TestCasePhaseDocumentationForPhaseWithInstructions, PhaseSequenceInfo, ExecutionEnvironmentInfo
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class BeforeAssertPhaseDocumentation(TestCasePhaseDocumentationForPhaseWithInstructions):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        super().__init__(name, instruction_set)
        self._tp = TextParser({
            'phase': phase_names.PHASE_NAME_DICTIONARY,
            'CWD': formatting.concept_(concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO),
        })

    def purpose(self) -> Description:
        return Description(self._tp.text(ONE_LINE_DESCRIPTION),
                           self._tp.fnap(REST_OF_DESCRIPTION))

    def sequence_info(self) -> PhaseSequenceInfo:
        return PhaseSequenceInfo(sequence_info__preceding_phase(phase_names.ACT),
                                 sequence_info__succeeding_phase(phase_names.ASSERT),
                                 prelude=sequence_info__not_executed_if_execution_mode_is_skip())

    def instruction_purpose_description(self) -> List[ParagraphItem]:
        return self._tp.fnap(INSTRUCTION_PURPOSE_DESCRIPTION)

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        previous = '{setup} phase'.format(setup=phase_names.SETUP.emphasis)
        return ExecutionEnvironmentInfo(
            cwd_at_start_of_phase_is_same_as_at_end_of_the(previous),
            prologue=execution_environment_prologue_for_post_act_phase(),
            environment_variables_prologue=env_vars_prologue_for_inherited_from_previous_phase())

    @property
    def _see_also_targets_specific(self) -> List[SeeAlsoTarget]:
        return [
            concepts.SDS_CONCEPT_INFO.cross_reference_target,
            concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.cross_reference_target,
            phase_infos.ACT.cross_reference_target,
            phase_infos.ASSERT.cross_reference_target,
        ]


ONE_LINE_DESCRIPTION = """\
Prepares for the {phase[assert]} phase.
"""

REST_OF_DESCRIPTION = """\
E.g. processing files and setting {CWD},
in order to make the assertions in the {phase[assert]} phase smooth.


Note that such preparations might as well be done as part of the {phase[assert]} phase.


Doing the preparations in this phase can make the {phase[assert]} phase cleaner, since
the {phase[assert]} phase then can consist solely of instructions that do "real" assertions
(as opposed to preparations for assertions).


The drawback is that if an instruction in this phase fails, then no assertions will have been
executed and one will not know if any of the assertions would pass.
"""

INSTRUCTION_PURPOSE_DESCRIPTION = """\
Each instruction should probably have some side effect that supports
the instructions in the {phase[assert]} phase.
"""
