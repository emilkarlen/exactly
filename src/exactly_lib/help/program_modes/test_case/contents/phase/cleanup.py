from exactly_lib.default.program_modes.test_case.default_instruction_names import EXECUTION_MODE_INSTRUCTION_NAME
from exactly_lib.execution.environment_variables import EXISTS_AT_BEFORE_ASSERT_MAIN
from exactly_lib.execution.execution_mode import NAME_SKIP
from exactly_lib.help.concepts.configuration_parameters.execution_mode import EXECUTION_MODE_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.plain_concepts.environment_variable import ENVIRONMENT_VARIABLE_CONCEPT
from exactly_lib.help.concepts.plain_concepts.sandbox import SANDBOX_CONCEPT
from exactly_lib.help.cross_reference_id import TestCasePhaseCrossReference, TestCasePhaseInstructionCrossReference
from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet
from exactly_lib.help.program_modes.test_case.contents.phase.utils import \
    pwd_at_start_of_phase_for_non_first_phases, sequence_info__not_executed_if_execution_mode_is_skip
from exactly_lib.help.program_modes.test_case.phase_help_contents_structures import \
    TestCasePhaseDocumentationForPhaseWithInstructions, PhaseSequenceInfo, ExecutionEnvironmentInfo
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.phase_names import phase_name_dictionary, ASSERT_PHASE_NAME, CONFIGURATION_PHASE_NAME
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure.structures import text


class CleanupPhaseDocumentation(TestCasePhaseDocumentationForPhaseWithInstructions):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        super().__init__(name, instruction_set)
        self.phase_name_dictionary = phase_name_dictionary()
        self.format_map = {
            'phase': phase_name_dictionary(),
            'SKIP': NAME_SKIP,
            'execution_mode': formatting.concept(EXECUTION_MODE_CONFIGURATION_PARAMETER.name().singular),
        }

    def purpose(self) -> Description:
        return Description(text(ONE_LINE_DESCRIPTION.format_map(self.format_map)),
                           self._parse(REST_OF_DESCRIPTION))

    def sequence_info(self) -> PhaseSequenceInfo:
        return PhaseSequenceInfo(self._parse(_SEQUENCE_INFO__PRECEDING_PHASE),
                                 self._parse(_SEQUENCE_INFO__SUCCEEDING_PHASE),
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
            EXECUTION_MODE_CONFIGURATION_PARAMETER.cross_reference_target(),
            TestCasePhaseCrossReference(ASSERT_PHASE_NAME.plain),
            TestCasePhaseInstructionCrossReference(CONFIGURATION_PHASE_NAME.plain,
                                                   EXECUTION_MODE_INSTRUCTION_NAME),
        ]

    def _parse(self, multi_line_string: str) -> list:
        return normalize_and_parse(multi_line_string.format_map(self.format_map))


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
