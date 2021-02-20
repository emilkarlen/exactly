from typing import List, Sequence

from exactly_lib import program_info
from exactly_lib.cli.definitions.common_cli_options import OPTION_FOR_ACTOR
from exactly_lib.definitions import test_case_file_structure as tc_fs, formatting, misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.concrete_cross_refs import PredefinedHelpContentsPartReference, \
    HelpPredefinedContentsPart
from exactly_lib.definitions.doc_format import literal_source_text
from exactly_lib.definitions.entity import concepts, conf_params, actors, directives, syntax_elements
from exactly_lib.definitions.formatting import InstructionName
from exactly_lib.definitions.test_case import phase_names, phase_infos
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.definitions.test_case.instructions.instruction_names import ACTOR_INSTRUCTION_NAME
from exactly_lib.help.program_modes.test_case.contents.phase.utils import \
    cwd_at_start_of_phase_for_non_first_phases, sequence_info__preceding_phase, \
    sequence_info__not_executed_if_execution_mode_is_skip, result_sub_dir_files_table, \
    sequence_info__succeeding_phase_of_act, timeout_prologue_for_inherited_from_previous_phase
from exactly_lib.help.program_modes.test_case.contents_structure.phase_documentation import \
    PhaseSequenceInfo, ExecutionEnvironmentInfo, \
    TestCasePhaseDocumentationForPhaseWithoutInstructions
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.structures import cell
from exactly_lib.util.textformat.structure.table import TableCell
from exactly_lib.util.textformat.textformat_parser import TextParser


class ActPhaseDocumentation(TestCasePhaseDocumentationForPhaseWithoutInstructions):
    def __init__(self, name: str):
        super().__init__(name)
        self._tp = TextParser({
            'program_name': program_info.PROGRAM_NAME,
            'phase': phase_names.PHASE_NAME_DICTIONARY,
            'setup': phase_infos.SETUP.name,
            'act': phase_infos.ACT.name,
            'action_to_check': concepts.ACTION_TO_CHECK_CONCEPT_INFO.name,
            'home_directory': formatting.conf_param_(conf_params.HDS_CASE_DIRECTORY_CONF_PARAM_INFO),
            'sandbox': formatting.concept_(concepts.SDS_CONCEPT_INFO),
            'result_dir': tc_fs.SDS_RESULT_INFO.identifier,
            'actor_option': OPTION_FOR_ACTOR,
            'actor': concepts.ACTOR_CONCEPT_INFO.name,
            'actor_instruction': formatting.InstructionName(ACTOR_INSTRUCTION_NAME),
            'default_actor': actors.DEFAULT_ACTOR_SINGLE_LINE_VALUE,
            'null_actor': formatting.entity_(actors.NULL_ACTOR),
            'os_process': misc_texts.OS_PROCESS_NAME,
            'instruction': concepts.INSTRUCTION_CONCEPT_INFO.name,
            'stdin_instruction': InstructionName(instruction_names.CONTENTS_OF_STDIN_INSTRUCTION_NAME),
            'env_instruction': InstructionName(instruction_names.ENV_VAR_INSTRUCTION_NAME),
            'timeout': concepts.TIMEOUT_CONCEPT_INFO.name,
            'timeout_default': concepts.TIMEOUT_CONCEPT_INFO.default,
            'timeout_instruction': InstructionName(instruction_names.TIMEOUT_INSTRUCTION_NAME),
            'conf_param': concepts.CONFIGURATION_PARAMETER_CONCEPT_INFO.name,
            'env_var': concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.name,
            'PROGRAM': syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name,
            'stdin': misc_texts.STDIN,

            'directive': concepts.DIRECTIVE_CONCEPT_INFO.name,
            'including': formatting.keyword(directives.INCLUDING_DIRECTIVE_INFO.singular_name),

        })

    def purpose(self) -> Description:
        return Description(self._tp.text(ONE_LINE_DESCRIPTION),
                           self._tp.fnap(REST_OF_DESCRIPTION) +
                           [result_sub_dir_files_table()] +
                           self._tp.fnap(_RELATION_TO_ACTOR__TO_BE_SEPARATE_SECTION))

    def sequence_info(self) -> PhaseSequenceInfo:
        return PhaseSequenceInfo(sequence_info__preceding_phase(phase_names.SETUP),
                                 sequence_info__succeeding_phase_of_act(),
                                 prelude=sequence_info__not_executed_if_execution_mode_is_skip())

    def contents_description(self) -> doc.SectionContents:
        initial_paragraphs = self._tp.fnap(_CONTENTS_DESCRIPTION) + [_escape_sequence_table()]
        return docs.section_contents(initial_paragraphs)

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        return ExecutionEnvironmentInfo(
            cwd_at_start_of_phase_for_non_first_phases(),
            environment_variables_prologue=self._tp.fnap(_ENV_VARS_DESCRIPTION),
            timeout_prologue=timeout_prologue_for_inherited_from_previous_phase(),
            custom_items=self._custom_environment_info_items())

    def _custom_environment_info_items(self) -> Sequence[docs.lists.HeaderContentListItem]:
        return [
            docs.list_item(
                misc_texts.STDIN.capitalize(),
                self._tp.fnap(_STDIN)
            ),
        ]

    @property
    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return [
            concepts.ACTOR_CONCEPT_INFO.cross_reference_target,
            concepts.ACTION_TO_CHECK_CONCEPT_INFO.cross_reference_target,
            concepts.SDS_CONCEPT_INFO.cross_reference_target,
            concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO.cross_reference_target,
            concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.cross_reference_target,
            concepts.TIMEOUT_CONCEPT_INFO.cross_reference_target,
            conf_params.ACTOR_CONF_PARAM_INFO.cross_reference_target,
            PredefinedHelpContentsPartReference(HelpPredefinedContentsPart.TEST_CASE_CLI),
            phase_infos.SETUP.cross_reference_target,
            phase_infos.BEFORE_ASSERT.cross_reference_target,
            phase_infos.ASSERT.cross_reference_target,
            phase_infos.SETUP.instruction_cross_reference_target(instruction_names.TIMEOUT_INSTRUCTION_NAME),
            phase_infos.SETUP.instruction_cross_reference_target(instruction_names.ENV_VAR_INSTRUCTION_NAME),
            phase_infos.SETUP.instruction_cross_reference_target(instruction_names.CONTENTS_OF_STDIN_INSTRUCTION_NAME),
        ]


_STDIN = """\
The contents set by the {stdin_instruction} {instruction}
in the {setup} phase.


If the {action_to_check:/q} is a {PROGRAM} that defines {stdin},
then the {stdin} set in the {setup:emphasis} phase is appended to the {stdin}
of the {PROGRAM}.


If not set in either way, {stdin} is empty.
"""

ONE_LINE_DESCRIPTION = """\
Contains the {action_to_check:/q}; executes it and stores the outcome for later inspection.
"""

REST_OF_DESCRIPTION = """\
Executes the {action_to_check:/q} as {os_process:a}.

Its outcome is stored as files in the {result_dir} directory of the {sandbox}:
"""

_RELATION_TO_ACTOR__TO_BE_SEPARATE_SECTION = """\
The {actor} configured for the test case
determines what the {act} phase will execute.


Default {actor} is: {default_actor}


If the {act} phase is not specified,
or if its contents is empty,
then the {null_actor} {actor} is used.
"""

_CONTENTS_DESCRIPTION = """\
The source of the {action_to_check:/q}.


The syntax depends on which {actor:/q} is used.


The {including} {directive} cannot be used.


Some escape sequences exist to make it possible to have contents that would otherwise be treated as
phase headers.

The escape sequences are only recognized at the first non-space characters of a line.
"""

_ENV_VARS_DESCRIPTION = """\
The {env_var:s} set for the {act:emphasis} phase.


The {env_instruction} {instruction} in the {setup:emphasis} phase
manipulates the {env_var:s} of the {act:emphasis} phase/{action_to_check:/q}.
"""


def _escape_sequence_table() -> docs.ParagraphItem:
    def _row(escape_sequence: str, translation: str) -> List[TableCell]:
        return [
            cell(docs.paras(literal_source_text(escape_sequence))),
            cell(docs.paras(literal_source_text(translation))),
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
