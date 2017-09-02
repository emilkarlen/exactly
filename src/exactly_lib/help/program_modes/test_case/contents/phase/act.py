from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import OPTION_FOR_ACTOR
from exactly_lib.help.concepts.configuration_parameters.actor import ACTOR_CONCEPT, HOW_TO_SPECIFY_ACTOR
from exactly_lib.help.concepts.configuration_parameters.home_case_directory import \
    HOME_CASE_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.plain_concepts.environment_variable import ENVIRONMENT_VARIABLE_CONCEPT
from exactly_lib.help.concepts.plain_concepts.sandbox import SANDBOX_CONCEPT
from exactly_lib.help.program_modes.test_case.contents.phase.utils import \
    sequence_info__succeeding_phase, \
    cwd_at_start_of_phase_for_non_first_phases, sequence_info__preceding_phase, env_vars_up_to_act, \
    sequence_info__not_executed_if_execution_mode_is_skip, result_sub_dir_files_table
from exactly_lib.help.program_modes.test_case.phase_help_contents_structures import \
    PhaseSequenceInfo, ExecutionEnvironmentInfo, \
    TestCasePhaseDocumentationForPhaseWithoutInstructions
from exactly_lib.help_texts.actors import all_actor_cross_refs
from exactly_lib.help_texts.cross_reference_id import TestCasePhaseCrossReference, \
    TestCasePhaseInstructionCrossReference, \
    TestSuiteSectionInstructionCrossReference
from exactly_lib.help_texts.names import formatting
from exactly_lib.help_texts.test_case.instructions.instruction_names import ACTOR_INSTRUCTION_NAME
from exactly_lib.help_texts.test_case.phase_names import phase_name_dictionary, SETUP_PHASE_NAME, \
    BEFORE_ASSERT_PHASE_NAME, \
    ASSERT_PHASE_NAME, CONFIGURATION_PHASE_NAME
from exactly_lib.help_texts.test_suite import formatted_section_names
from exactly_lib.test_case_file_structure import sandbox_directory_structure as sds
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.structures import cell


class ActPhaseDocumentation(TestCasePhaseDocumentationForPhaseWithoutInstructions):
    def __init__(self,
                 name: str):
        super().__init__(name)
        self.phase_name_dictionary = phase_name_dictionary()
        self.format_map = {
            'phase': phase_name_dictionary(),
            'home_directory': formatting.concept(HOME_CASE_DIRECTORY_CONFIGURATION_PARAMETER.name().singular),
            'actor': formatting.concept(HOME_CASE_DIRECTORY_CONFIGURATION_PARAMETER.name().singular),
            'sandbox': formatting.concept(SANDBOX_CONCEPT.name().singular),
            'result_subdir': sds.SUB_DIRECTORY__RESULT,
            'actor_option': OPTION_FOR_ACTOR,
            'actor_concept': formatting.concept(ACTOR_CONCEPT.singular_name()),
            'actor_instruction': formatting.InstructionName(ACTOR_INSTRUCTION_NAME),
        }

    def purpose(self) -> Description:
        from exactly_lib.help.actors.all_actor_docs import DEFAULT_ACTOR_DOC
        actor_info = (self._parse(_DESCRIPTION__BEFORE_DEFAULT_ACTOR_DESCRIPTION) +
                      docs.paras(DEFAULT_ACTOR_DOC.name_and_single_line_description()) +
                      self._parse(HOW_TO_SPECIFY_ACTOR)
                      )
        return Description(docs.text(ONE_LINE_DESCRIPTION.format_map(self.format_map)),
                           self._parse(REST_OF_DESCRIPTION) +
                           [result_sub_dir_files_table()] +
                           actor_info)

    def sequence_info(self) -> PhaseSequenceInfo:
        return PhaseSequenceInfo(sequence_info__preceding_phase(SETUP_PHASE_NAME),
                                 sequence_info__succeeding_phase(self.phase_name_dictionary,
                                                                 BEFORE_ASSERT_PHASE_NAME),
                                 prelude=sequence_info__not_executed_if_execution_mode_is_skip())

    def is_mandatory(self) -> bool:
        return True

    def contents_description(self) -> doc.SectionContents:
        initial_paragraphs = self._parse(_CONTENTS_DESCRIPTION) + [_escape_sequence_table()]
        return docs.section_contents(initial_paragraphs)

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        return ExecutionEnvironmentInfo(cwd_at_start_of_phase_for_non_first_phases(),
                                        env_vars_up_to_act())

    @property
    def see_also(self) -> list:
        from exactly_lib.help.concepts.configuration_parameters.actor import ACTOR_CONCEPT
        return [
                   ACTOR_CONCEPT.cross_reference_target(),
                   SANDBOX_CONCEPT.cross_reference_target(),
                   ENVIRONMENT_VARIABLE_CONCEPT.cross_reference_target(),
                   HOME_CASE_DIRECTORY_CONFIGURATION_PARAMETER.cross_reference_target(),
                   TestCasePhaseCrossReference(SETUP_PHASE_NAME.plain),
                   TestCasePhaseCrossReference(BEFORE_ASSERT_PHASE_NAME.plain),
                   TestCasePhaseCrossReference(ASSERT_PHASE_NAME.plain),
                   TestCasePhaseInstructionCrossReference(CONFIGURATION_PHASE_NAME.plain,
                                                          ACTOR_INSTRUCTION_NAME),
                   TestSuiteSectionInstructionCrossReference(formatted_section_names.CONFIGURATION_SECTION_NAME.plain,
                                                             ACTOR_INSTRUCTION_NAME),
               ] + all_actor_cross_refs()

    def _parse(self, multi_line_string: str) -> list:
        return normalize_and_parse(multi_line_string.format_map(self.format_map))


ONE_LINE_DESCRIPTION = """\
The action to check/system under test (SUT).
"""

REST_OF_DESCRIPTION = """\
The program specified by the {phase[act]} phase is executed and its result is stored
in the {result_subdir}/ sub directory of the {sandbox}:
"""

_DESCRIPTION__BEFORE_DEFAULT_ACTOR_DESCRIPTION = """\
The meaning and syntax of the {phase[act]} phase depends on which {actor_concept} is used.


The default {actor_concept} is:
"""

_CONTENTS_DESCRIPTION = """\
Some escape sequences exist to make it possible to have contents that would otherwise be treated as
phase headers.

The escape sequences are only recognized at the first non-space characters of a line.
"""


def _escape_sequence_table() -> docs.ParagraphItem:
    def _row(escape_sequence: str, translation: str) -> list:
        return [
            cell(docs.paras(escape_sequence)),
            cell(docs.paras(translation)),
        ]

    return docs.first_row_is_header_table(
        [
            [
                cell(docs.paras('Source')),
                cell(docs.paras('Translation')),
            ]] +
        [
            _row('\\[', '['),
            _row('\\\\', '\\'),
        ],
        '  ')
