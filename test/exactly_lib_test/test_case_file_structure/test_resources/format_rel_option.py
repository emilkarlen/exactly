"""
Deprecated util to format relativity options.

Introduced for helping change option syntax from --option to -option
"""
from exactly_lib.definitions import file_ref


def format_rel_options(template: str) -> str:
    return template.format_map(FORMAT_MAP)


FORMAT_MAP = {
    'rel_tmp': file_ref.REL_TMP_OPTION,
    'rel_act': file_ref.REL_ACT_OPTION,
    'rel_result': file_ref.REL_RESULT_OPTION,
    'rel_cd': file_ref.REL_CWD_OPTION,
    'rel_case_home': file_ref.REL_HOME_CASE_OPTION,
    'rel_act_home': file_ref.REL_HOME_ACT_OPTION,
    'rel_symbol': file_ref.REL_symbol_OPTION,
    'rel_source_file': file_ref.REL_source_file_dir_OPTION,
}
