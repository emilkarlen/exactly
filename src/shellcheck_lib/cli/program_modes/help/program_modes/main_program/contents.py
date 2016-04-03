from shellcheck_lib.cli.program_modes.help import argument_parsing
from shellcheck_lib.util.textformat.parse import normalize_and_parse
from shellcheck_lib.util.textformat.structure import lists
from shellcheck_lib.util.textformat.structure.core import ParagraphItem, Text
from shellcheck_lib.util.textformat.structure.lists import HeaderContentListItem


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
            _help(argument_parsing.TEST_CASE),
            normalize_and_parse(
                'Describes the Test Case functionality.')),
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
        HeaderContentListItem(
            _help(argument_parsing.TEST_SUITE),
            normalize_and_parse(
                'Describes the Test Suite functionality.')),
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


def _help(syntax: str) -> Text:
    return Text(argument_parsing.HELP + ' ' + syntax)
