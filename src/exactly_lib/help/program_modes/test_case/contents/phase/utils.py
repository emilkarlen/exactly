from typing import List

from exactly_lib.definitions import test_case_file_structure, formatting, misc_texts
from exactly_lib.definitions.doc_format import file_name_text
from exactly_lib.definitions.entity import concepts, conf_params
from exactly_lib.definitions.formatting import SectionName
from exactly_lib.definitions.test_case.phase_names import PHASE_NAME_DICTIONARY
from exactly_lib.tcfs import sds as sds, tcds_symbols
from exactly_lib.tcfs.tcds_symbols import SYMBOL_RESULT
from exactly_lib.test_case.test_case_status import NAME_SKIP
from exactly_lib.util.textformat.structure import structures as docs, table
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.table import TableCell
from exactly_lib.util.textformat.textformat_parser import TextParser

_TEXT_PARSER = TextParser({
    'instruction': concepts.INSTRUCTION_CONCEPT_INFO.name,
    'act_dir': test_case_file_structure.SDS_ACT_INFO.identifier,
    'cwd': formatting.concept_(concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO),
    'execution_mode': formatting.conf_param_(conf_params.TEST_CASE_STATUS_CONF_PARAM_INFO),
    'SKIP': NAME_SKIP,
    'result_subdir': sds.SUB_DIRECTORY__RESULT,
    'sandbox': formatting.concept_(concepts.SDS_CONCEPT_INFO),
    'SYMBOL_RESULT': SYMBOL_RESULT,
    'phase': PHASE_NAME_DICTIONARY,
    'ATC': formatting.concept_(concepts.ACTION_TO_CHECK_CONCEPT_INFO),
    'SYMBOL': formatting.concept_(concepts.SYMBOL_CONCEPT_INFO),
    'env_var': concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.name,
    'timeout': concepts.TIMEOUT_CONCEPT_INFO.name,
})


def cwd_at_start_of_phase_for_configuration_phase() -> List[ParagraphItem]:
    return []


def cwd_at_start_of_phase_first_phase_executed_in_the_sandbox() -> List[ParagraphItem]:
    return _TEXT_PARSER.fnap(_CWD_AT_START_OF_PHASE_FIRST_PHASE_EXECUTED_IN_THE_SANDBOX)


def cwd_at_start_of_phase_is_same_as_at_end_of_the(previous: str) -> List[ParagraphItem]:
    return _TEXT_PARSER.fnap(
        _CWD_AT_START_OF_PHASE_IS_SAME_AS_AT_END_OF_THE,
        {'previous': previous}
    )


def cwd_at_start_of_phase_for_non_first_phases() -> List[ParagraphItem]:
    return cwd_at_start_of_phase_is_same_as_at_end_of_the('previous phase')


def env_vars_prologue_for_inherited_from_previous_phase() -> List[ParagraphItem]:
    return _TEXT_PARSER.fnap(ENV_VARS_PROLOGUE_FOR_INHERITED_FROM_PREVIOUS_PHASE)


def timeout_prologue_for_inherited_from_previous_phase() -> List[ParagraphItem]:
    return _TEXT_PARSER.fnap(TIMEOUT_PROLOGUE_FOR_INHERITED_FROM_PREVIOUS_PHASE)


def symbols_for_configuration_phase() -> List[str]:
    return []


def symbols_up_to_act() -> List[str]:
    return tcds_symbols.SET_AT_SETUP__SYMBOLS + tcds_symbols.SET_AT_SDS__SYMBOLS


def symbols_after_act() -> List[str]:
    return symbols_up_to_act() + tcds_symbols.SET_AT_BEFORE_ASSERT__SYMBOLS


def sequence_info__not_executed_if_execution_mode_is_skip() -> List[ParagraphItem]:
    return _TEXT_PARSER.fnap(_SEQUENCE_INFO__NOT_EXECUTED_IF_EXECUTION_MODE_IS_SKIP)


def sequence_info__succeeding_phase(following_phase: SectionName) -> List[ParagraphItem]:
    return _TEXT_PARSER.fnap(_SEQUENCE_INFO__SUCCEEDING_PHASE,
                             {'following_phase': following_phase}
                             )


def sequence_info__succeeding_phase_of_act() -> List[ParagraphItem]:
    return _TEXT_PARSER.fnap(_SEQUENCE_INFO__SUCCEEDING_PHASE_OF_ACT)


def sequence_info__preceding_phase(following_phase: SectionName) -> List[ParagraphItem]:
    return _TEXT_PARSER.fnap(_SEQUENCE_INFO__PRECEDING_PHASE,
                             {'following_phase': following_phase}
                             )


def result_sub_dir_files_table() -> docs.ParagraphItem:
    def row(name: str, file_name: str) -> List[TableCell]:
        return [docs.cell(docs.paras(name)),
                docs.cell(docs.paras(file_name_text(sds.SUB_DIRECTORY__RESULT + '/' + file_name)))]

    rows = [
        row(misc_texts.EXIT_CODE.singular, sds.RESULT_FILE__EXITCODE),
        row(misc_texts.STDOUT, sds.RESULT_FILE__STDOUT),
        row(misc_texts.STDERR, sds.RESULT_FILE__STDERR),
    ]

    return table.Table(table.TableFormat(first_column_is_header=True),
                       rows)


def execution_environment_prologue_for_post_act_phase() -> List[ParagraphItem]:
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

_SEQUENCE_INFO__SUCCEEDING_PHASE_OF_ACT = """\
If the {ATC} cannot be executed, then execution jumps to the {phase[cleanup]} phase,
and the test case halts with an error.

Otherwise, the {phase[before_assert]} phase follows.
"""

_ENVIRONMENT_PROLOGUE_POST_ACT_RESULT_DIR = """\
{instruction:s/u} have access to the result of the {ATC} via
the files in the {result_subdir}/ sub directory of the {sandbox}:
"""

_ENVIRONMENT_PROLOGUE_POST_ACT_RESULT_ENV_VARIABLE = """\
The value of the {SYMBOL_RESULT} {SYMBOL} is the absolute path of
the {result_subdir}/ directory.
"""

ENV_VARS_PROLOGUE_FOR_INHERITED_FROM_PREVIOUS_PHASE = """\
{env_var:s/u} are inherited from the previous phase.
"""

TIMEOUT_PROLOGUE_FOR_INHERITED_FROM_PREVIOUS_PHASE = """\
{timeout:/u} is inherited from the previous phase.
"""
