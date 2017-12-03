from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet
from exactly_lib.help.program_modes.test_case.contents.phase.utils import \
    sequence_info__succeeding_phase, \
    sequence_info__preceding_phase, \
    sequence_info__not_executed_if_execution_mode_is_skip, execution_environment_prologue_for_post_act_phase, \
    cwd_at_start_of_phase_is_same_as_at_end_of_the
from exactly_lib.help.program_modes.test_case.phase_help_contents_structures import \
    TestCasePhaseDocumentationForPhaseWithInstructions, PhaseSequenceInfo, ExecutionEnvironmentInfo
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.cross_ref.concrete_cross_refs import TestCasePhaseCrossReference
from exactly_lib.help_texts.entity import concepts
from exactly_lib.help_texts.test_case.phase_names import ACT_PHASE_NAME, ASSERT_PHASE_NAME, \
    SETUP_PHASE_NAME, PHASE_NAME_DICTIONARY
from exactly_lib.test_case_file_structure.environment_variables import EXISTS_AT_BEFORE_ASSERT_MAIN
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.textformat_parser import TextParser


class BeforeAssertPhaseDocumentation(TestCasePhaseDocumentationForPhaseWithInstructions):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        super().__init__(name, instruction_set)
        self._tp = TextParser({
            'phase': PHASE_NAME_DICTIONARY,
            'CWD': formatting.concept_(concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO),
        })

    def purpose(self) -> Description:
        return Description(self._tp.text(ONE_LINE_DESCRIPTION),
                           self._tp.fnap(REST_OF_DESCRIPTION))

    def sequence_info(self) -> PhaseSequenceInfo:
        return PhaseSequenceInfo(sequence_info__preceding_phase(ACT_PHASE_NAME),
                                 sequence_info__succeeding_phase(ASSERT_PHASE_NAME),
                                 prelude=sequence_info__not_executed_if_execution_mode_is_skip())

    def is_mandatory(self) -> bool:
        return False

    def instruction_purpose_description(self) -> list:
        return self._tp.fnap(INSTRUCTION_PURPOSE_DESCRIPTION)

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        previous = '{setup} phase'.format(setup=SETUP_PHASE_NAME.emphasis)
        return ExecutionEnvironmentInfo(cwd_at_start_of_phase_is_same_as_at_end_of_the(previous),
                                        EXISTS_AT_BEFORE_ASSERT_MAIN,
                                        prologue=execution_environment_prologue_for_post_act_phase())

    @property
    def see_also_targets(self) -> list:
        return [
            concepts.SANDBOX_CONCEPT_INFO.cross_reference_target,
            concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.cross_reference_target,
            TestCasePhaseCrossReference(ACT_PHASE_NAME.plain),
            TestCasePhaseCrossReference(ASSERT_PHASE_NAME.plain),
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
