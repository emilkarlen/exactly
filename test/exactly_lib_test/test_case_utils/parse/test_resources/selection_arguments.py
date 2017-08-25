from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.parse import parse_file_selector
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.parse import token


def selection_arguments(name_option_pattern: str = '',
                        type_selection: FileType = None,
                        named_selector: str = '') -> str:
    """
    Gives the CLI argument and options for selection of given
    selectors
    :param name_option_pattern: Name selector, or nothing, if empty string.
    :param type_selection: Type selector, or nothing, if None
    :returns str: Empty string iff no selector is given.
    """
    the_selectors_arguments = selectors_arguments(name_option_pattern,
                                                  type_selection,
                                                  named_selector)
    if the_selectors_arguments:
        selector_option = option_syntax.option_syntax(parse_file_selector.SELECTION_OPTION.name)
        return selector_option + ' ' + the_selectors_arguments
    else:
        return ''


def selectors_arguments(name_pattern: str = '',
                        type_selection: FileType = None,
                        named_selector: str = '',
                        ) -> str:
    """
    Gives the CLI argument and options for the given selectors

    :param named_selector: A named (reference to a) selector
    :param name_pattern: Name selector, or nothing, if empty string.
    :param type_selection: Type selector, or nothing, if None
    :returns str: Empty string iff no selector is given.
    """
    selectors = []

    if name_pattern:
        selectors.append(name_selector_of(name_pattern))
    if type_selection:
        selectors.append(type_selector_of(type_selection))
    if named_selector:
        selectors.append(named_selector)

    and_combinator = ' ' + parse_file_selector.AND_OPERATOR + ' '
    return and_combinator.join(selectors)


def name_selector_of(pattern: str) -> str:
    pattern_arg = pattern
    if ' ' in pattern_arg and pattern_arg[0] not in token.QUOTE_CHARS:
        pattern_arg = token.HARD_QUOTE_CHAR + pattern_arg + token.HARD_QUOTE_CHAR

    return parse_file_selector.COMMAND_NAME__NAME_SELECTOR + ' ' + pattern_arg


def type_selector_of(file_type: file_properties.FileType) -> str:
    return parse_file_selector.COMMAND_NAME__TYPE_SELECTOR + \
           ' ' + \
           file_properties.TYPE_INFO[file_type].type_argument
