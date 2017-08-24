from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.parse import parse_file_selector
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib_test.test_case_utils.parse import parse_file_selector as parse_test


def selection_arguments(name_option_pattern: str = '',
                        type_selection: FileType = None) -> str:
    """
    Gives the CLI argument and options for selection of given
    selectors
    :param name_option_pattern: Name selector, or nothing, if empty string.
    :param type_selection: Type selector, or nothing, if None
    """
    ret_val = ''

    if name_option_pattern or type_selection:
        ret_val = option_syntax.option_syntax(parse_file_selector.SELECTION_OPTION.name)
        if name_option_pattern:
            ret_val = ret_val + ' ' + parse_test.name_selector_of(name_option_pattern)
        if type_selection:
            if name_option_pattern:
                ret_val = ret_val + ' ' + parse_file_selector.AND_OPERATOR
            ret_val = ret_val + ' ' + parse_test.type_selector_of(type_selection)

    return ret_val
