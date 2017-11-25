import types

from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet, InstructionGroup
from exactly_lib.help.program_modes.test_case.contents.phase.utils import \
    cwd_at_start_of_phase_for_non_first_phases, sequence_info__preceding_phase, \
    sequence_info__not_executed_if_execution_mode_is_skip, execution_environment_prologue_for_post_act_phase
from exactly_lib.help.program_modes.test_case.phase_help_contents_structures import \
    TestCasePhaseDocumentationForPhaseWithInstructions, PhaseSequenceInfo, ExecutionEnvironmentInfo
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.cross_reference_id import TestCasePhaseCrossReference
from exactly_lib.help_texts.entity import concepts
from exactly_lib.help_texts.test_case.phase_names import BEFORE_ASSERT_PHASE_NAME, \
    CLEANUP_PHASE_NAME, PHASE_NAME_DICTIONARY
from exactly_lib.processing import exit_values
from exactly_lib.test_case.phases.assert_ import AssertPhasePurpose, WithAssertPhasePurpose
from exactly_lib.test_case_file_structure import sandbox_directory_structure as sds
from exactly_lib.test_case_file_structure.environment_variables import EXISTS_AT_BEFORE_ASSERT_MAIN, ENV_VAR_RESULT
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.textformat_parser import TextParser


def _mk_assertions_group(instructions: list) -> InstructionGroup:
    return InstructionGroup('Assertions',
                            'assertion',
                            _TEXT_PARSER.fnap(_ASSERTION_INSTRUCTIONS_DESCRIPTION),
                            instructions)


def _mk_both_group(instructions: list) -> InstructionGroup:
    return InstructionGroup('Assertions and helpers',
                            'both',
                            _TEXT_PARSER.fnap(_BOTH_INSTRUCTIONS_DESCRIPTION),
                            instructions)


def _mk_helpers_group(instructions: list) -> InstructionGroup:
    return InstructionGroup('Helpers',
                            'helper',
                            _TEXT_PARSER.fnap(_HELPER_INSTRUCTIONS_DESCRIPTION),
                            instructions)


_MK_GROUP_DICT = {
    AssertPhasePurpose.ASSERTION: _mk_assertions_group,
    AssertPhasePurpose.HELPER: _mk_helpers_group,
    AssertPhasePurpose.BOTH: _mk_both_group,
}

_TEXT_PARSER = TextParser({
    'phase': PHASE_NAME_DICTIONARY,
    'PASS': exit_values.EXECUTION__PASS.exit_identifier,
    'FAIL': exit_values.EXECUTION__FAIL.exit_identifier,
    'HARD_ERROR': exit_values.EXECUTION__HARD_ERROR.exit_identifier,
    'result_subdir': sds.SUB_DIRECTORY__RESULT,
    'sandbox': formatting.concept_(concepts.SANDBOX_CONCEPT_INFO),
    'ENV_VAR_RESULT': ENV_VAR_RESULT,
})


class AssertPhaseDocumentation(TestCasePhaseDocumentationForPhaseWithInstructions):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        super().__init__(name, instruction_set)

    def purpose(self) -> Description:
        return Description(_TEXT_PARSER.text(ONE_LINE_DESCRIPTION),
                           _TEXT_PARSER.fnap(REST_OF_DESCRIPTION))

    def sequence_info(self) -> PhaseSequenceInfo:
        return PhaseSequenceInfo(sequence_info__preceding_phase(BEFORE_ASSERT_PHASE_NAME),
                                 _TEXT_PARSER.fnap(_SEQUENCE_INFO__SUCCEEDING_PHASE),
                                 prelude=sequence_info__not_executed_if_execution_mode_is_skip())

    def is_mandatory(self) -> bool:
        return False

    def instruction_purpose_description(self) -> list:
        return _TEXT_PARSER.fnap(INSTRUCTION_PURPOSE_DESCRIPTION)

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        return ExecutionEnvironmentInfo(cwd_at_start_of_phase_for_non_first_phases(),
                                        EXISTS_AT_BEFORE_ASSERT_MAIN,
                                        prologue=execution_environment_prologue_for_post_act_phase())

    @property
    def instruction_group_by(self) -> types.FunctionType:
        return _instruction_group_by

    @property
    def see_also_targets(self) -> list:
        return [
            concepts.SANDBOX_CONCEPT_INFO.cross_reference_target,
            concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.cross_reference_target,
            TestCasePhaseCrossReference(BEFORE_ASSERT_PHASE_NAME.plain),
            TestCasePhaseCrossReference(CLEANUP_PHASE_NAME.plain),
        ]


def _instruction_group_by(instr_docs: list) -> list:
    purpose_2_instructions = dict([
        (value, [])
        for value in AssertPhasePurpose
    ])
    for doc in instr_docs:
        assert isinstance(doc, WithAssertPhasePurpose), str(type(doc))
        purpose_2_instructions[doc.assert_phase_purpose].append(doc)

    ret_val = []
    for p in AssertPhasePurpose:
        instructions = purpose_2_instructions[p]
        if instructions:
            ret_val.append(_MK_GROUP_DICT[p](instructions))

    return ret_val


ONE_LINE_DESCRIPTION = """\
Assertions on the outcome of the system under test (the {phase[act]} phase) that determine
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
All instructions in the {phase[assert]} phase are assertions that either {PASS} or {FAIL}.


In practice, though, some instructions may have more of a purpose of "preparation"
for an assertion.

Such a preparation might be to sort a file that the system under test (SUT) has produced,
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


Note. This is job that could perhaps be done in {phase[before_assert]:syntax}. 
"""
