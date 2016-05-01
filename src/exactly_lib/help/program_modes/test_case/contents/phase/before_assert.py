from exactly_lib.execution.environment_variables import EXISTS_AT_BEFORE_ASSERT_MAIN
from exactly_lib.help.concepts.plain_concepts.environment_variable import ENVIRONMENT_VARIABLE_CONCEPT
from exactly_lib.help.concepts.plain_concepts.sandbox import SANDBOX_CONCEPT
from exactly_lib.help.cross_reference_id import TestCasePhaseCrossReference
from exactly_lib.help.program_modes.test_case.contents.phase.utils import \
    sequence_info__succeeding_phase, \
    pwd_at_start_of_phase_for_non_first_phases, sequence_info__preceding_phase, \
    sequence_info__not_executed_if_execution_mode_is_skip
from exactly_lib.help.program_modes.test_case.contents_structure import TestCasePhaseInstructionSet
from exactly_lib.help.program_modes.test_case.phase_help_contents_structures import \
    TestCasePhaseDocumentationForPhaseWithInstructions, PhaseSequenceInfo, ExecutionEnvironmentInfo
from exactly_lib.help.utils.description import Description
from exactly_lib.help.utils.phase_names import phase_name_dictionary, ACT_PHASE_NAME, ASSERT_PHASE_NAME
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure.structures import text


class BeforeAssertPhaseDocumentation(TestCasePhaseDocumentationForPhaseWithInstructions):
    def __init__(self,
                 name: str,
                 instruction_set: TestCasePhaseInstructionSet):
        super().__init__(name, instruction_set)
        self.phase_name_dictionary = phase_name_dictionary()
        self.format_map = {
            'phase': phase_name_dictionary()
        }

    def purpose(self) -> Description:
        return Description(text(ONE_LINE_DESCRIPTION.format_map(self.format_map)),
                           self._parse(REST_OF_DESCRIPTION))

    def sequence_info(self) -> PhaseSequenceInfo:
        return PhaseSequenceInfo(sequence_info__preceding_phase(ACT_PHASE_NAME),
                                 sequence_info__succeeding_phase(self.phase_name_dictionary,
                                                                 ASSERT_PHASE_NAME),
                                 prelude=sequence_info__not_executed_if_execution_mode_is_skip())

    def is_mandatory(self) -> bool:
        return False

    def instruction_purpose_description(self) -> list:
        return self._parse(INSTRUCTION_PURPOSE_DESCRIPTION)

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        return ExecutionEnvironmentInfo(pwd_at_start_of_phase_for_non_first_phases(),
                                        EXISTS_AT_BEFORE_ASSERT_MAIN)

    @property
    def see_also(self) -> list:
        return [
            SANDBOX_CONCEPT.cross_reference_target(),
            ENVIRONMENT_VARIABLE_CONCEPT.cross_reference_target(),
            TestCasePhaseCrossReference(ACT_PHASE_NAME.plain),
            TestCasePhaseCrossReference(ASSERT_PHASE_NAME.plain),
        ]

    def _parse(self, multi_line_string: str) -> list:
        return normalize_and_parse(multi_line_string.format_map(self.format_map))


ONE_LINE_DESCRIPTION = """\
Prepares for the {phase[assert]} phase.
"""

REST_OF_DESCRIPTION = """\
E.g. processing files and setting Present Working Directory,
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
