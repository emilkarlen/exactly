from exactly_lib.cli.program_modes.help import argument_parsing
from exactly_lib.cli.program_modes.help import arguments_for
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure.core import ParagraphItem, Text, StringText
from exactly_lib.util.textformat.structure.lists import HeaderContentListItem


def help_invokation_variants() -> ParagraphItem:
    items = [
        HeaderContentListItem(
            _help(argument_parsing.HELP),
            normalize_and_parse('Displays this help.')),
        HeaderContentListItem(
            _help(''),
            normalize_and_parse(
                'Describes the program.')),
        HeaderContentListItem(
            _help(argument_parsing.HTML_DOCUMENTATION),
            normalize_and_parse(
                'Generates a HTML version of all help information available in the program.')),
        _item(_help_args(arguments_for.test_case_overview()),
              'Describes the Test Case functionality.'),
        _item(_help_args(arguments_for.test_case_cli_syntax()),
              'Describes the Test Case command line syntax.'),
        HeaderContentListItem(
            _help(argument_parsing.CONCEPT),
            normalize_and_parse(
                'Lists all concepts.')),
        HeaderContentListItem(
            _help(argument_parsing.CONCEPT + ' CONCEPT'),
            normalize_and_parse(
                'Describes a given concept.')),
        HeaderContentListItem(
            _help(argument_parsing.INSTRUCTIONS),
            normalize_and_parse(
                'Lists test-case instructions per phase.')),
        HeaderContentListItem(
            _help('PHASE'),
            normalize_and_parse(
                'Describes a given Test Case phase.')),
        HeaderContentListItem(
            _help('PHASE ' + argument_parsing.INSTRUCTIONS),
            normalize_and_parse(
                'Lists instructions for a Test Case phase.')),
        HeaderContentListItem(
            _help('PHASE INSTRUCTION'),
            normalize_and_parse(
                'Describes a given Test Case instruction in a given Phase.')),
        HeaderContentListItem(
            _help('INSTRUCTION'),
            normalize_and_parse(
                'Describes all Test Case instructions with the given name.')),
        _item(_help_args(arguments_for.test_suite_overview()),
              'Describes the Test Suite functionality.'),
        _item(_help_args(arguments_for.test_suite_cli_syntax()),
              'Describes the Test Suite command line syntax.'),
        HeaderContentListItem(
            _help(argument_parsing.TEST_SUITE + ' SECTION'),
            normalize_and_parse(
                'Describes a given Test Suite section.')),
    ]

    return un_indented_variable_list(items)


def un_indented_variable_list(items: list,
                              custom_separations: lists.Separations = lists.Separations(1, 0)) -> ParagraphItem:
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST,
                                                custom_separations=custom_separations,
                                                custom_indent_spaces=0))


def _item(cmd_line: Text, text_str: str) -> HeaderContentListItem:
    return HeaderContentListItem(cmd_line, normalize_and_parse(text_str))


def _help(syntax: str) -> Text:
    return StringText(argument_parsing.HELP + ' ' + syntax)


def _help_args(args: list) -> Text:
    return StringText(argument_parsing.HELP + ' ' + ' '.join(args))
