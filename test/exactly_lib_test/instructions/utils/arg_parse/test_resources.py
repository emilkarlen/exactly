from exactly_lib.test_case_file_structure import relative_path_options


def args_with_rel_ops(arg_str: str, **kwargs) -> str:
    if kwargs:
        format_map = dict(list(_FORMAT_MAP.items()) + list(kwargs.items()))
        return arg_str.format_map(format_map)
    return arg_str.format_map(_FORMAT_MAP)


_FORMAT_MAP = {
    'rel_home_option': relative_path_options.REL_HOME_OPTION,
    'rel_cwd_option': relative_path_options.REL_CWD_OPTION,
    'rel_tmp_option': relative_path_options.REL_TMP_OPTION,
    'rel_act_option': relative_path_options.REL_ACT_OPTION,
    'rel_result_option': relative_path_options.REL_RESULT_OPTION,
}
