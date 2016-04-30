from exactly_lib.execution.environment_variables import EXISTS_AT_SETUP_MAIN
from exactly_lib.help.concepts.concept import SANDBOX_CONCEPT, ENVIRONMENT_VARIABLE_CONCEPT
from exactly_lib.help.program_modes.test_case.contents.phase.utils import \
    pwd_at_start_of_phase_first_phase_executed_in_the_sandbox
from exactly_lib.help.program_modes.test_case.contents_structure import TestCasePhaseInstructionSet
from exactly_lib.help.program_modes.test_case.phase_help_contents_structures import \
    TestCasePhaseDocumentationForPhaseWithInstructions, PhaseSequenceInfo, ExecutionEnvironmentInfo
from exactly_lib.help.utils.description import Description
from exactly_lib.help.utils.phase_names import phase_name_dictionary
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure.structures import text


class SetupPhaseDocumentation(TestCasePhaseDocumentationForPhaseWithInstructions):
    def __init__(self,
                 name: str,
                 instruction_set: TestCasePhaseInstructionSet):
        super().__init__(name, instruction_set)
        self.format_map = {
            'phase': phase_name_dictionary()
        }

    def purpose(self) -> Description:
        return Description(text(ONE_LINE_DESCRIPTION.format_map(self.format_map)),
                           self._parse(REST_OF_DESCRIPTION))

    def sequence_info(self) -> PhaseSequenceInfo:
        return PhaseSequenceInfo(self._parse(SEQUENCE_INFO__PRECEDING_PHASE),
                                 self._parse(SEQUENCE_INFO__SUCCEEDING_PHASE))

    def is_mandatory(self) -> bool:
        return False

    def instruction_purpose_description(self) -> list:
        return self._parse(INSTRUCTION_PURPOSE_DESCRIPTION)

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        return ExecutionEnvironmentInfo(pwd_at_start_of_phase_first_phase_executed_in_the_sandbox(),
                                        EXISTS_AT_SETUP_MAIN)

    @property
    def see_also(self) -> list:
        return [
            SANDBOX_CONCEPT.cross_reference_target(),
            ENVIRONMENT_VARIABLE_CONCEPT.cross_reference_target(),
        ]

    def _parse(self, multi_line_string: str) -> list:
        return normalize_and_parse(multi_line_string.format_map(self.format_map))


ONE_LINE_DESCRIPTION = """\
Sets up the environment that the system under test
(the {phase[act]} phase) will be executed in.
"""

REST_OF_DESCRIPTION = """\
E.g. populating the PWD with files and directories,
setting the contents of stdin,
setting environment variables,
or populating external resources such as databases.
"""

INSTRUCTION_PURPOSE_DESCRIPTION = """
Each instruction should probably have some side effect that affects
the system under test (the {phase[act]} phase)."""

SEQUENCE_INFO__PRECEDING_PHASE = """
This phase follows the {phase[conf]} phase,
and is the first phase that is executed in the sandbox."""

SEQUENCE_INFO__SUCCEEDING_PHASE = """\
If any of the instructions fail, then the {phase[cleanup]} phase is executed,
and the test case halts with an error.

Otherwise, the {phase[act]} phase follows.
"""
