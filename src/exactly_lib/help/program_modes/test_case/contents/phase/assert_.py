from typing import List, Callable

from exactly_lib.definitions import formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.test_case import phase_names, phase_infos
from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet, InstructionGroup
from exactly_lib.help.program_modes.test_case.contents.phase.utils import \
    cwd_at_start_of_phase_for_non_first_phases, sequence_info__preceding_phase, \
    sequence_info__not_executed_if_execution_mode_is_skip, execution_environment_prologue_for_post_act_phase, \
    env_vars_prologue_for_inherited_from_previous_phase, timeout_prologue_for_inherited_from_previous_phase
from exactly_lib.help.program_modes.test_case.contents_structure.phase_documentation import \
    TestCasePhaseDocumentationForPhaseWithInstructions, PhaseSequenceInfo, ExecutionEnvironmentInfo
from exactly_lib.processing import exit_values
from exactly_lib.tcfs import sds as sds
from exactly_lib.tcfs.tcds_symbols import SYMBOL_RESULT
from exactly_lib.test_case.phases.assert_ import AssertPhasePurpose, WithAssertPhasePurpose
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.lists import ListType
from exactly_lib.util.textformat.textformat_parser import TextParser


class AssertPhaseDocumentation(TestCasePhaseDocumentationForPhaseWithInstructions):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        super().__init__(name, instruction_set)
        self._tp = TextParser({
            'phase': phase_names.PHASE_NAME_DICTIONARY,
            'PASS': exit_values.EXECUTION__PASS.exit_identifier,
            'FAIL': exit_values.EXECUTION__FAIL.exit_identifier,
            'HARD_ERROR': exit_values.EXECUTION__HARD_ERROR.exit_identifier,
            'result_subdir': sds.SUB_DIRECTORY__RESULT,
            'sandbox': formatting.concept_(concepts.SDS_CONCEPT_INFO),
            'ENV_VAR_RESULT': SYMBOL_RESULT,
            'ATC': formatting.concept_(concepts.ACTION_TO_CHECK_CONCEPT_INFO),
        })

    def purpose(self) -> Description:
        return Description(self._tp.text(ONE_LINE_DESCRIPTION),
                           self._tp.fnap(REST_OF_DESCRIPTION))

    def sequence_info(self) -> PhaseSequenceInfo:
        return PhaseSequenceInfo(sequence_info__preceding_phase(phase_names.BEFORE_ASSERT),
                                 self._tp.fnap(_SEQUENCE_INFO__SUCCEEDING_PHASE),
                                 prelude=sequence_info__not_executed_if_execution_mode_is_skip())

    def instruction_purpose_description(self) -> List[docs.ParagraphItem]:
        paragraphs = self._tp.fnap(INSTRUCTION_PURPOSE_DESCRIPTION)
        paragraphs += self._instruction_groups_list()
        return paragraphs

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        return ExecutionEnvironmentInfo(
            cwd_at_start_of_phase_for_non_first_phases(),
            prologue=execution_environment_prologue_for_post_act_phase(),
            environment_variables_prologue=env_vars_prologue_for_inherited_from_previous_phase(),
            timeout_prologue=timeout_prologue_for_inherited_from_previous_phase())

    @property
    def instruction_group_by(self) -> Callable[[List[WithAssertPhasePurpose]], List[InstructionGroup]]:
        return self._instruction_group_by

    @property
    def _see_also_targets_specific(self) -> List[SeeAlsoTarget]:
        return [
            concepts.SDS_CONCEPT_INFO.cross_reference_target,
            concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO.cross_reference_target,
            concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.cross_reference_target,
            concepts.TIMEOUT_CONCEPT_INFO.cross_reference_target,
            phase_infos.BEFORE_ASSERT.cross_reference_target,
            phase_infos.CLEANUP.cross_reference_target,
        ]

    def _instruction_group_by(self, instr_docs: List[WithAssertPhasePurpose]) -> List[InstructionGroup]:
        purpose_2_instructions = {
            value: []
            for value in AssertPhasePurpose
        }
        for doc in instr_docs:
            assert isinstance(doc, WithAssertPhasePurpose), str(type(doc))
            purpose_2_instructions[doc.assert_phase_purpose].append(doc)

        ret_val = []
        for p in AssertPhasePurpose:
            instructions = purpose_2_instructions[p]
            if instructions:
                ret_val.append(self._group_of(p, instructions))

        return ret_val

    def _group_of(self, purpose_type: AssertPhasePurpose, instructions: list) -> InstructionGroup:
        info = _INSTRUCTION_TYPES[purpose_type]

        return InstructionGroup(info[0],
                                info[1],
                                self._tp.fnap(info[2]),
                                instructions)

    def _instruction_groups_list(self) -> List[docs.ParagraphItem]:
        def item(purpose: AssertPhasePurpose) -> lists.HeaderContentListItem:
            info = _INSTRUCTION_TYPES[purpose]
            return docs.list_item(info[0],
                                  self._tp.fnap(info[2]))

        return [
            docs.simple_list_with_space_between_elements_and_content(map(item, list(AssertPhasePurpose)),
                                                                     ListType.ITEMIZED_LIST)
        ]


ONE_LINE_DESCRIPTION = """\
Assertions on the outcome of the {ATC} (the {phase[act]} phase) that determine
the outcome of the test case.
"""

REST_OF_DESCRIPTION = """\
If any of the instructions in this phase {FAIL}, then the outcome of the test
case is {FAIL}, otherwise it is {PASS}.


An exception to the above is if an instruction encounters an unexpected problem that makes it
neither {PASS} nor {FAIL}, in which case the outcome of the test case will indicate
this unexpected problem instead of {PASS} or {FAIL}.
"""

INSTRUCTION_PURPOSE_DESCRIPTION = """\
Every instructions in the {phase[assert]} phase is an assertion that 
report its outcome as either {PASS} or {FAIL}.


If an instruction encounter a problem that prevents it from completing its work,
it reports this as {HARD_ERROR}.


In practice, though, some instructions may have more of a purpose of "preparation"
for an assertion - they are helpers for the assertions.

Such a preparation might be to sort a file that the {ATC} has produced,
so that it's possible to compare it with a constant file containing the expected sorted output, e.g.


This kind of preparation can also be done in the {phase[before_assert]} phase,
but it might be more suitable to put it in the {phase[assert]} phase right
before the instruction that does the "true" assertion.
"""

_SEQUENCE_INFO__SUCCEEDING_PHASE = """\
This phase is followed by the {phase[cleanup]} phase.


If any of the instructions {FAIL}, remaining instructions in the phase will be skipped
and the execution will jump directly to the {phase[cleanup]} phase.
"""

_ASSERTION_INSTRUCTIONS_DESCRIPTION = """\
Instructions that serve as assertions.
"""

_BOTH_INSTRUCTIONS_DESCRIPTION = """\
Instructions that may serve as either an assertion or a helper for an assertion.
"""

_HELPER_INSTRUCTIONS_DESCRIPTION = """\
Instructions that prepare things for assertion instructions,
and that are not assertions in them selves.


Typically, if these instructions cannot do their job, they report {HARD_ERROR},
instead of {FAIL}.


Note that the preparation done by such an instruction can perhaps be done in {phase[before_assert]:syntax}. 
"""

_INSTRUCTION_TYPES = {
    AssertPhasePurpose.ASSERTION: ('Assertions',
                                   'assertion',
                                   _ASSERTION_INSTRUCTIONS_DESCRIPTION),
    AssertPhasePurpose.BOTH: ('Assertions and helpers',
                              'both',
                              _BOTH_INSTRUCTIONS_DESCRIPTION),
    AssertPhasePurpose.HELPER: ('Helpers',
                                'helper',
                                _HELPER_INSTRUCTIONS_DESCRIPTION),
}
