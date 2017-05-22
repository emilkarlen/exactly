from exactly_lib.help_texts import file_ref as file_ref_texts


def args_with_rel_ops(arg_str: str, **kwargs) -> str:
    if kwargs:
        format_map = dict(list(_FORMAT_MAP.items()) + list(kwargs.items()))
        return arg_str.format_map(format_map)
    return arg_str.format_map(_FORMAT_MAP)


_FORMAT_MAP = {
    'rel_home_option': file_ref_texts.REL_HOME_OPTION,
    'rel_cwd_option': file_ref_texts.REL_CWD_OPTION,
    'rel_tmp_option': file_ref_texts.REL_TMP_OPTION,
    'rel_act_option': file_ref_texts.REL_ACT_OPTION,
    'rel_result_option': file_ref_texts.REL_RESULT_OPTION,
}


def rel_symbol_arg_str(symbol_name: str) -> str:
    return file_ref_texts.REL_symbol_OPTION + ' ' + symbol_name
