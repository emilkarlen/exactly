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
                'Describes the test-case functionality.')),
        HeaderContentListItem(
            _help(argument_parsing.INSTRUCTIONS),
            normalize_and_parse(
                'Lists instructions per test-case phase.')),
        HeaderContentListItem(
            _help('PHASE'),
            normalize_and_parse(
                'Help for a test-case phase.')),
        HeaderContentListItem(
            _help('PHASE ' + argument_parsing.INSTRUCTIONS),
            normalize_and_parse(
                'Lists instructions for a test-case phase.')),
        HeaderContentListItem(
            _help('PHASE INSTRUCTION'),
            normalize_and_parse(
                'Describes a test-case instruction in a phase.')),
        HeaderContentListItem(
            _help('INSTRUCTION'),
            normalize_and_parse(
                'Help for an test-case instruction (in any phase).')),
        HeaderContentListItem(
            _help(argument_parsing.TEST_SUITE),
            normalize_and_parse(
                'Describes the test-suite functionality.')),
        HeaderContentListItem(
            _help(argument_parsing.TEST_SUITE + ' SECTION'),
            normalize_and_parse(
                'Describes a test-suite section.')),
    ]

    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST,
                                                custom_separations=lists.Separations(1, 0),
                                                custom_indent_spaces=0))


def _help(syntax: str) -> Text:
    return Text(argument_parsing.HELP + ' ' + syntax)
