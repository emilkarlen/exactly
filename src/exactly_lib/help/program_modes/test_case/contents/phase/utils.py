from exactly_lib.execution import environment_variables
from exactly_lib.execution.environment_variables import ENV_VAR_RESULT
from exactly_lib.execution.execution_mode import NAME_SKIP
from exactly_lib.help.concepts.configuration_parameters.execution_mode import EXECUTION_MODE_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.plain_concepts.present_working_directory import PRESENT_WORKING_DIRECTORY_CONCEPT
from exactly_lib.help.concepts.plain_concepts.sandbox import SANDBOX_CONCEPT
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.formatting import SectionName
from exactly_lib.test_case import sandbox_directory_structure as sds
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs, table


def pwd_at_start_of_phase_for_configuration_phase() -> list:
    return []


def pwd_at_start_of_phase_first_phase_executed_in_the_sandbox() -> list:
    text = """\
    At the beginning of the phase, the {pwd}
    is the {act_dir}/ sub directory of the sandbox.
    """
    return normalize_and_parse(text.format(act_dir=sds.SUB_DIRECTORY__ACT,
                                           pwd=formatting.concept(PRESENT_WORKING_DIRECTORY_CONCEPT.name().singular)))


def pwd_at_start_of_phase_is_same_as_at_end_of_the(previous: str) -> list:
    text = """\
    The {pwd} is the same as at the end of the {previous}.

    (which is the {act_dir}/ sub directory of the sandbox, if it has not been changed.)
    """
    return normalize_and_parse(text.format(act_dir=sds.SUB_DIRECTORY__ACT,
                                           pwd=formatting.concept(PRESENT_WORKING_DIRECTORY_CONCEPT.name().singular),
                                           previous=previous))


def pwd_at_start_of_phase_for_non_first_phases() -> list:
    return pwd_at_start_of_phase_is_same_as_at_end_of_the('previous phase')


def env_vars_for_configuration_phase() -> list:
    return []


def env_vars_up_to_act() -> list:
    return environment_variables.SET_AT_SETUP__ENV_VARS + environment_variables.SET_AT_EDS__ENV_VARS


def env_vars_after_act() -> list:
    return env_vars_up_to_act() + environment_variables.SET_AT_BEFORE_ASSERT__ENV_VARS


def sequence_info__not_executed_if_execution_mode_is_skip() -> list:
    return normalize_and_parse(_SEQUENCE_INFO__NOT_EXECUTED_IF_EXECUTION_MODE_IS_SKIP.format(
        execution_mode=EXECUTION_MODE_CONFIGURATION_PARAMETER.name().singular,
        SKIP=NAME_SKIP,
    ))


def sequence_info__succeeding_phase(phase_name_dictionary: dict,
                                    following_phase: SectionName) -> list:
    return normalize_and_parse(_SEQUENCE_INFO__SUCCEEDING_PHASE.format(phase=phase_name_dictionary,
                                                                       following_phase=following_phase))


_SEQUENCE_INFO__SUCCEEDING_PHASE = """\
If any of the instructions fail, the execution jumps to the {phase[cleanup]} phase,
and the test case halts with an error.

Otherwise, the {following_phase} phase follows.
"""


def sequence_info__preceding_phase(following_phase: SectionName) -> list:
    return normalize_and_parse(_SEQUENCE_INFO__PRECEDING_PHASE.format(following_phase=following_phase))


_SEQUENCE_INFO__PRECEDING_PHASE = """\
This phase is executed directly after the {following_phase} phase.
"""

_SEQUENCE_INFO__NOT_EXECUTED_IF_EXECUTION_MODE_IS_SKIP = """\
If the {execution_mode} is set to {SKIP}, then this phase is not executed.

Otherwise:
"""


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
    format_map = {
        'result_subdir': sds.SUB_DIRECTORY__RESULT,
        'sandbox': SANDBOX_CONCEPT.name().singular,
        'ENV_VAR_RESULT': ENV_VAR_RESULT,
    }
    return (normalize_and_parse(_ENVIRONMENT_PROLOGUE_POST_ACT_RESULT_DIR.format_map(format_map)) +
            [result_sub_dir_files_table()] +
            normalize_and_parse(_ENVIRONMENT_PROLOGUE_POST_ACT_RESULT_ENV_VARIABLE.format_map(format_map)))


_ENVIRONMENT_PROLOGUE_POST_ACT_RESULT_DIR = """\
Instructions have access to the result of the SUT via
the files in the {result_subdir}/ sub directory of the {sandbox}:
"""
_ENVIRONMENT_PROLOGUE_POST_ACT_RESULT_ENV_VARIABLE = """\
The value of the {ENV_VAR_RESULT} environment variable is the absolute path of
the {result_subdir}/ directory.
"""
