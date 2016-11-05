from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import OPTION_FOR_ACTOR
from exactly_lib.help.concepts.configuration_parameters.home_directory import HOME_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.plain_concepts.environment_variable import ENVIRONMENT_VARIABLE_CONCEPT
from exactly_lib.help.concepts.plain_concepts.sandbox import SANDBOX_CONCEPT
from exactly_lib.help.cross_reference_id import TestCasePhaseCrossReference
from exactly_lib.help.program_modes.test_case.contents.phase.utils import \
    sequence_info__succeeding_phase, \
    pwd_at_start_of_phase_for_non_first_phases, sequence_info__preceding_phase, env_vars_up_to_act, \
    sequence_info__not_executed_if_execution_mode_is_skip, result_sub_dir_files_table
from exactly_lib.help.program_modes.test_case.phase_help_contents_structures import \
    PhaseSequenceInfo, ExecutionEnvironmentInfo, \
    TestCasePhaseDocumentationForPhaseWithoutInstructions
from exactly_lib.help.utils.phase_names import phase_name_dictionary, SETUP_PHASE_NAME, BEFORE_ASSERT_PHASE_NAME, \
    ASSERT_PHASE_NAME
from exactly_lib.test_case import sandbox_directory_structure as sds
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs


class ActPhaseDocumentation(TestCasePhaseDocumentationForPhaseWithoutInstructions):
    def __init__(self,
                 name: str):
        super().__init__(name)
        self.phase_name_dictionary = phase_name_dictionary()
        self.format_map = {
            'phase': phase_name_dictionary(),
            'home_directory': HOME_DIRECTORY_CONFIGURATION_PARAMETER.name().singular,
            'sandbox': SANDBOX_CONCEPT.name().singular,
            'result_subdir': sds.SUB_DIRECTORY__RESULT,
            'actor_option': OPTION_FOR_ACTOR,
        }

    def purpose(self) -> Description:
        return Description(docs.text(ONE_LINE_DESCRIPTION.format_map(self.format_map)),
                           self._parse(REST_OF_DESCRIPTION) +
                           [result_sub_dir_files_table()])

    def sequence_info(self) -> PhaseSequenceInfo:
        return PhaseSequenceInfo(sequence_info__preceding_phase(SETUP_PHASE_NAME),
                                 sequence_info__succeeding_phase(self.phase_name_dictionary,
                                                                 BEFORE_ASSERT_PHASE_NAME),
                                 prelude=sequence_info__not_executed_if_execution_mode_is_skip())

    def is_mandatory(self) -> bool:
        return True

    def contents_description(self) -> list:
        return self._parse(_CONTENTS_DESCRIPTION)

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        return ExecutionEnvironmentInfo(pwd_at_start_of_phase_for_non_first_phases(),
                                        env_vars_up_to_act())

    @property
    def see_also(self) -> list:
        return [
            SANDBOX_CONCEPT.cross_reference_target(),
            ENVIRONMENT_VARIABLE_CONCEPT.cross_reference_target(),
            HOME_DIRECTORY_CONFIGURATION_PARAMETER.cross_reference_target(),
            TestCasePhaseCrossReference(SETUP_PHASE_NAME.plain),
            TestCasePhaseCrossReference(BEFORE_ASSERT_PHASE_NAME.plain),
            TestCasePhaseCrossReference(ASSERT_PHASE_NAME.plain),
        ]

    def _parse(self, multi_line_string: str) -> list:
        return normalize_and_parse(multi_line_string.format_map(self.format_map))


ONE_LINE_DESCRIPTION = """\
The system under test (SUT).
"""

REST_OF_DESCRIPTION = """\
The program specified by the {phase[act]} phase is executed and its result is stored
in the {result_subdir}/ sub directory of the {sandbox}:
"""

_CONTENTS_DESCRIPTION = """\
By default, the {phase[act]} phase should contain exactly one command line.


This command line uses shell syntax for quoting and separation of elements.


The first element must be the path of an existing, executable file.


If the path is relative, then it is taken to be relative the {home_directory}.


The the path is not found, then this will cause a VALIDATION error, and the test case will not be executed.


The {actor_option} option can be used to specify a different setup of the {phase[act]} phase.
"""
