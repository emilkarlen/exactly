from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import OPTION_FOR_ACTOR
from exactly_lib.definitions import test_case_file_structure as tc_fs, formatting
from exactly_lib.definitions.cross_ref.concrete_cross_refs import TestCasePhaseCrossReference
from exactly_lib.definitions.entity import concepts, conf_params, actors
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.definitions.test_case.instructions.instruction_names import ACTOR_INSTRUCTION_NAME
from exactly_lib.help.entities.concepts.objects.actor import HOW_TO_SPECIFY_ACTOR
from exactly_lib.help.program_modes.test_case.contents.phase.utils import \
    sequence_info__succeeding_phase, \
    cwd_at_start_of_phase_for_non_first_phases, sequence_info__preceding_phase, env_vars_up_to_act, \
    sequence_info__not_executed_if_execution_mode_is_skip, result_sub_dir_files_table, \
    env_vars_prologue_for_inherited_from_previous_phase
from exactly_lib.help.program_modes.test_case.contents_structure.phase_documentation import \
    PhaseSequenceInfo, ExecutionEnvironmentInfo, \
    TestCasePhaseDocumentationForPhaseWithoutInstructions
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.structures import cell
from exactly_lib.util.textformat.textformat_parser import TextParser


class ActPhaseDocumentation(TestCasePhaseDocumentationForPhaseWithoutInstructions):
    def __init__(self, name: str):
        super().__init__(name)
        self._tp = TextParser({
            'phase': phase_names.PHASE_NAME_DICTIONARY,
            'action_to_check': formatting.concept_(concepts.ACTION_TO_CHECK_CONCEPT_INFO),
            'home_directory': formatting.conf_param_(conf_params.HOME_CASE_DIRECTORY_CONF_PARAM_INFO),
            'sandbox': formatting.concept_(concepts.SANDBOX_CONCEPT_INFO),
            'result_dir': tc_fs.SDS_RESULT_INFO.identifier,
            'actor_option': OPTION_FOR_ACTOR,
            'actor_concept': formatting.concept_(concepts.ACTOR_CONCEPT_INFO),
            'actor_instruction': formatting.InstructionName(ACTOR_INSTRUCTION_NAME),
            'default_actor': actors.DEFAULT_ACTOR_SINGLE_LINE_VALUE,
            'null_actor': formatting.entity_(actors.NULL_ACTOR),
        })

    def purpose(self) -> Description:
        actor_info = (self._tp.fnap(_DESCRIPTION__BEFORE_HOW_TO_SPECIFY_ACTOR) +
                      self._tp.fnap(HOW_TO_SPECIFY_ACTOR)
                      )
        return Description(self._tp.text(ONE_LINE_DESCRIPTION),
                           self._tp.fnap(REST_OF_DESCRIPTION) +
                           [result_sub_dir_files_table()] +
                           actor_info)

    def sequence_info(self) -> PhaseSequenceInfo:
        return PhaseSequenceInfo(sequence_info__preceding_phase(phase_names.SETUP),
                                 sequence_info__succeeding_phase(phase_names.BEFORE_ASSERT),
                                 prelude=sequence_info__not_executed_if_execution_mode_is_skip())

    def contents_description(self) -> doc.SectionContents:
        initial_paragraphs = self._tp.fnap(_CONTENTS_DESCRIPTION) + [_escape_sequence_table()]
        return docs.section_contents(initial_paragraphs)

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        return ExecutionEnvironmentInfo(
            cwd_at_start_of_phase_for_non_first_phases(),
            env_vars_up_to_act(),
            environment_variables_prologue=env_vars_prologue_for_inherited_from_previous_phase())

    @property
    def see_also_targets(self) -> list:
        return [
            concepts.ACTOR_CONCEPT_INFO.cross_reference_target,
            concepts.SANDBOX_CONCEPT_INFO.cross_reference_target,
            concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.cross_reference_target,
            TestCasePhaseCrossReference(phase_names.SETUP.plain),
            TestCasePhaseCrossReference(phase_names.BEFORE_ASSERT.plain),
            TestCasePhaseCrossReference(phase_names.ASSERT.plain),
            actors.NULL_ACTOR.cross_reference_target,
            actors.DEFAULT_ACTOR.cross_reference_target,
        ]


ONE_LINE_DESCRIPTION = """\
The {action_to_check} (or "system under test").
"""

REST_OF_DESCRIPTION = """\
Specifies an action that is checked by the test case.


There are a number of different kind of actions:


 * executable program
 * source file
 * source code
 * shell command


Which one is used -
and the meaning and syntax of the {phase[act]} phase -
depends on which {actor_concept} is used.


The action specified by the {phase[act]} phase is executed and its result is stored
in the {result_dir} directory of the {sandbox}:
"""

_DESCRIPTION__BEFORE_HOW_TO_SPECIFY_ACTOR = """\
If a test case does not have an {phase[act]} phase,
or if the {phase[act]} phase is empty,
then the {null_actor} {actor_concept} is used.


For test cases with a non-empty {phase[act]} phase, the default {actor_concept} is:


{default_actor}
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
