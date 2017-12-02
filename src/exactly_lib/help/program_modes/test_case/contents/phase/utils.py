from exactly_lib.help_texts import test_case_file_structure, formatting
from exactly_lib.help_texts.entity import concepts, conf_params
from exactly_lib.help_texts.formatting import SectionName
from exactly_lib.help_texts.test_case.phase_names import PHASE_NAME_DICTIONARY
from exactly_lib.test_case.test_case_status import NAME_SKIP
from exactly_lib.test_case_file_structure import sandbox_directory_structure as sds, environment_variables
from exactly_lib.test_case_file_structure.environment_variables import ENV_VAR_RESULT
from exactly_lib.util.textformat.structure import structures as docs, table
from exactly_lib.util.textformat.textformat_parser import TextParser

_TEXT_PARSER = TextParser({
    'act_dir': test_case_file_structure.SDS_ACT_INFO.identifier,
    'cwd': formatting.concept_(concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO),
    'execution_mode': formatting.conf_param_(conf_params.TEST_CASE_STATUS_CONF_PARAM_INFO),
    'SKIP': NAME_SKIP,
    'result_subdir': sds.SUB_DIRECTORY__RESULT,
    'sandbox': formatting.concept_(concepts.SANDBOX_CONCEPT_INFO),
    'ENV_VAR_RESULT': ENV_VAR_RESULT,
    'phase': PHASE_NAME_DICTIONARY,
})


def cwd_at_start_of_phase_for_configuration_phase() -> list:
    return []


def cwd_at_start_of_phase_first_phase_executed_in_the_sandbox() -> list:
    return _TEXT_PARSER.fnap(_CWD_AT_START_OF_PHASE_FIRST_PHASE_EXECUTED_IN_THE_SANDBOX)


def cwd_at_start_of_phase_is_same_as_at_end_of_the(previous: str) -> list:
    return _TEXT_PARSER.fnap(
        _CWD_AT_START_OF_PHASE_IS_SAME_AS_AT_END_OF_THE,
        {'previous': previous}
    )


def cwd_at_start_of_phase_for_non_first_phases() -> list:
    return cwd_at_start_of_phase_is_same_as_at_end_of_the('previous phase')


def env_vars_for_configuration_phase() -> list:
    return []


def env_vars_up_to_act() -> list:
    return environment_variables.SET_AT_SETUP__ENV_VARS + environment_variables.SET_AT_SDS__ENV_VARS


def env_vars_after_act() -> list:
    return env_vars_up_to_act() + environment_variables.SET_AT_BEFORE_ASSERT__ENV_VARS


def sequence_info__not_executed_if_execution_mode_is_skip() -> list:
    return _TEXT_PARSER.fnap(_SEQUENCE_INFO__NOT_EXECUTED_IF_EXECUTION_MODE_IS_SKIP)


def sequence_info__succeeding_phase(following_phase: SectionName) -> list:
    return _TEXT_PARSER.fnap(_SEQUENCE_INFO__SUCCEEDING_PHASE,
                             {'following_phase': following_phase}
                             )


def sequence_info__preceding_phase(following_phase: SectionName) -> list:
    return _TEXT_PARSER.fnap(_SEQUENCE_INFO__PRECEDING_PHASE,
                             {'following_phase': following_phase}
                             )


def result_sub_dir_files_table() -> docs.ParagraphItem:
    def row(name: str, file_name: str):
        return [docs.cell(docs.paras(name)),
                docs.cell(docs.paras(sds.SUB_DIRECTORY__RESULT + '/' + file_name))]

    rows = [
        row('exit code', sds.RESULT_FILE__EXITCODE),
        row('stdout', sds.RESULT_FILE__STDOUT),
        row('stderr', sds.RESULT_FILE__STDERR),
    ]

    return table.Table(table.TableFormat(first_column_is_header=True),
                       rows)


def execution_environment_prologue_for_post_act_phase() -> list:
    return (
        _TEXT_PARSER.fnap(_ENVIRONMENT_PROLOGUE_POST_ACT_RESULT_DIR) +
        [result_sub_dir_files_table()] +
        _TEXT_PARSER.fnap(_ENVIRONMENT_PROLOGUE_POST_ACT_RESULT_ENV_VARIABLE)
    )


_CWD_AT_START_OF_PHASE_FIRST_PHASE_EXECUTED_IN_THE_SANDBOX = """\
At the beginning of the phase, the {cwd}
is the {act_dir} directory in the {sandbox}.
"""

_CWD_AT_START_OF_PHASE_IS_SAME_AS_AT_END_OF_THE = """\
The {cwd} is the same as at the end of the {previous}.

(which is the {act_dir} directory in the {sandbox}, if it has not been changed.)
"""

_SEQUENCE_INFO__PRECEDING_PHASE = """\
This phase is executed directly after the {following_phase} phase.
"""

_SEQUENCE_INFO__NOT_EXECUTED_IF_EXECUTION_MODE_IS_SKIP = """\
If the {execution_mode} is set to {SKIP}, then this phase is not executed.

Otherwise:
"""

_SEQUENCE_INFO__SUCCEEDING_PHASE = """\
If any of the instructions fail, then execution jumps to the {phase[cleanup]} phase,
and the test case halts with an error.

Otherwise, the {following_phase} phase follows.
"""

_ENVIRONMENT_PROLOGUE_POST_ACT_RESULT_DIR = """\
Instructions have access to the result of the SUT via
the files in the {result_subdir}/ sub directory of the {sandbox}:
"""

_ENVIRONMENT_PROLOGUE_POST_ACT_RESULT_ENV_VARIABLE = """\
The value of the {ENV_VAR_RESULT} environment variable is the absolute path of
the {result_subdir}/ directory.
"""
