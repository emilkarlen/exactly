from exactly_lib.definitions import path as path_texts


def args_with_rel_ops(arg_str: str, **kwargs) -> str:
    if kwargs:
        format_map = dict(list(_FORMAT_MAP.items()) + list(kwargs.items()))
        return arg_str.format_map(format_map)
    return arg_str.format_map(_FORMAT_MAP)


_FORMAT_MAP = {
    'rel_home_option': path_texts.REL_HOME_CASE_OPTION,
    'rel_cwd_option': path_texts.REL_CWD_OPTION,
    'rel_tmp_option': path_texts.REL_TMP_OPTION,
    'rel_act_option': path_texts.REL_ACT_OPTION,
    'rel_result_option': path_texts.REL_RESULT_OPTION,
}


def rel_symbol_arg_str(symbol_name: str) -> str:
    return path_texts.REL_symbol_OPTION + ' ' + symbol_name
