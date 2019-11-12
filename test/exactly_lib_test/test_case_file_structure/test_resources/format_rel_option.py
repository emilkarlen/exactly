"""
Deprecated util to format relativity options.

Introduced for helping change option syntax from --option to -option
"""
from exactly_lib.definitions import path


def format_rel_options(template: str) -> str:
    return template.format_map(FORMAT_MAP)


FORMAT_MAP = {
    'rel_tmp': path.REL_TMP_OPTION,
    'rel_act': path.REL_ACT_OPTION,
    'rel_result': path.REL_RESULT_OPTION,
    'rel_cd': path.REL_CWD_OPTION,
    'rel_case_home': path.REL_HOME_CASE_OPTION,
    'rel_act_home': path.REL_HOME_ACT_OPTION,
    'rel_symbol': path.REL_symbol_OPTION,
    'rel_source_file': path.REL_source_file_dir_OPTION,
}
