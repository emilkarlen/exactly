"""Functionality for accessing a subset of the files in a directory."""
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, InvokationVariant
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.name_and_cross_ref import Name
from exactly_lib.instructions.utils.err_msg import property_description
from exactly_lib.named_element.file_selectors import FileSelectorConstant
from exactly_lib.named_element.resolver_structure import FileSelectorResolver
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils import file_properties, token_stream_parse_prime
from exactly_lib.test_case_utils.token_stream_parse_prime import TokenParserPrime
from exactly_lib.type_system_values.file_selector import FileSelector
from exactly_lib.util import dir_contents_selection
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.dir_contents_selection import Selectors
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs

SELECTION_OF_ALL_FILES = FileSelectorConstant(FileSelector(dir_contents_selection.all_files()))

CONCEPT_NAME = Name('selector', 'selectors')

COMMAND_NAME__NAME_SELECTOR = 'name'

COMMAND_NAME__TYPE_SELECTOR = 'type'


class CommandSetup:
    def __init__(self, argument_syntax_element_name: str):
        self.argument_syntax_element_name = argument_syntax_element_name


COMMANDS = {
    COMMAND_NAME__NAME_SELECTOR: CommandSetup('PATTERN'),
    COMMAND_NAME__TYPE_SELECTOR: CommandSetup('TYPE'),
}

AND_OPERATOR = '&'

SELECTOR_ARGUMENT = a.Named('SELECTOR')

SELECTION_OPTION = a.option(long_name='selection',
                            argument=SELECTOR_ARGUMENT.name)

SELECTION = a.Named('SELECTION')


def selection_syntax_element_description() -> SyntaxElementDescription:
    return cl_syntax.cli_argument_syntax_element_description(
        SELECTION,
        docs.paras(_SELECTION_DESCRIPTION),
        [
            InvokationVariant(cl_syntax.arg_syntax(SELECTION_OPTION)),
        ]
    )


def selector_syntax_element_description() -> SyntaxElementDescription:
    return cl_syntax.cli_argument_syntax_element_description(
        SELECTOR_ARGUMENT,
        [],
        [
            InvokationVariant(cl_syntax.cl_syntax_for_args([
                a.Single(a.Multiplicity.MANDATORY,
                         a.Constant(COMMAND_NAME__NAME_SELECTOR)),
                a.Single(a.Multiplicity.MANDATORY,
                         a.Named(COMMANDS[COMMAND_NAME__NAME_SELECTOR].argument_syntax_element_name)),
            ]),
                _fnap(_NAME_SELECTOR_SED_DESCRIPTION)
            ),
            InvokationVariant(cl_syntax.cl_syntax_for_args([
                a.Single(a.Multiplicity.MANDATORY,
                         a.Constant(COMMAND_NAME__TYPE_SELECTOR)),
                a.Single(a.Multiplicity.MANDATORY,
                         a.Named(COMMANDS[COMMAND_NAME__TYPE_SELECTOR].argument_syntax_element_name)),
            ]),
                _type_selector_sed_description()
            ),
            InvokationVariant(cl_syntax.cl_syntax_for_args([
                a.Single(a.Multiplicity.MANDATORY,
                         SELECTOR_ARGUMENT),
                a.Single(a.Multiplicity.MANDATORY,
                         a.Constant(AND_OPERATOR)),
                a.Single(a.Multiplicity.MANDATORY,
                         SELECTOR_ARGUMENT),
            ]),
                _fnap(_AND_SELECTOR_SED_DESCRIPTION)
            ),
        ]
    )


class SelectorsDescriptor(property_description.ErrorMessagePartConstructor):
    def __init__(self, resolver: FileSelectorResolver):
        self.resolver = resolver

    def lines(self, environment: InstructionEnvironmentForPostSdsStep) -> list:
        selectors = self.resolver.resolve(environment.symbols).selectors
        descriptions = selectors.selection_descriptions
        if not descriptions:
            return []
        separator = ' ' + AND_OPERATOR + ' '
        description = separator.join(selectors.selection_descriptions)
        line = SELECTION.name.capitalize() + ' : ' + description
        return [line]


def every_file_in_dir() -> Selectors:
    return dir_contents_selection.all_files()


def parse_from_parse_source(source: ParseSource) -> Selectors:
    with token_stream_parse_prime.from_parse_source(source) as tp:
        return parse(tp)


def parse_resolver_from_parse_source(source: ParseSource) -> FileSelectorResolver:
    with token_stream_parse_prime.from_parse_source(source) as tp:
        return parse_resolver(tp)


def parse_optional_selection_option_from_parse_source(source: ParseSource) -> Selectors:
    with token_stream_parse_prime.from_parse_source(source) as tp:
        return parse_optional_selection_option(tp)


def parse_optional_selection_option(parser: TokenParserPrime) -> Selectors:
    return parser.consume_and_handle_optional_option(
        dir_contents_selection.all_files(),
        parse,
        SELECTION_OPTION.name)


def parse_optional_selection_resolver(parser: TokenParserPrime) -> FileSelectorResolver:
    return parser.consume_and_handle_optional_option(
        SELECTION_OF_ALL_FILES,
        parse_resolver,
        SELECTION_OPTION.name)


def parse_resolver(parser: TokenParserPrime) -> FileSelectorResolver:
    """
    :return: None iff selector is not mandatory and there were no arguments in the source.
    """
    selectors = parse(parser)
    return FileSelectorConstant(FileSelector(selectors))


def parse(parser: TokenParserPrime) -> Selectors:
    """
    :return: If selector is not mandatory, and source is not a selector: a selector of all files
    :raises `SingleInstructionInvalidArgumentException`: selector is mandatory but source is not a selector
    """
    parser = token_stream_parse_prime.token_parser_with_additional_error_message_format_map(
        parser,
        ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS)

    def parse_mandatory_simple() -> Selectors:
        return parser.parse_mandatory_command(_SELECTOR_PARSERS,
                                              'Missing {_SELECTOR_} argument.')

    ret_val = parse_mandatory_simple()

    while parser.consume_optional_constant_string_that_must_be_unquoted_and_equal(AND_OPERATOR):
        next_selector = parse_mandatory_simple()
        ret_val = dir_contents_selection.and_also(ret_val, next_selector)

    return ret_val


def _error_message(template: str) -> str:
    return template.format_map(ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS)


def _parse_name_selector(parser: TokenParserPrime) -> Selectors:
    pattern = parser.consume_mandatory_string_argument(
        _ERR_MSG_FORMAT_STRING_FOR_PARSE_NAME)
    return dir_contents_selection.name_matches_pattern(pattern)


def _parse_type_selector(parser: TokenParserPrime) -> Selectors:
    file_type = parser.consume_mandatory_constant_string_that_must_be_unquoted_and_equal(
        file_properties.SYNTAX_TOKEN_2_FILE_TYPE,
        file_properties.SYNTAX_TOKEN_2_FILE_TYPE.get,
        '{_TYPE_}')
    return dir_contents_selection.file_type_is(file_type)


_SELECTOR_PARSERS = {
    COMMAND_NAME__NAME_SELECTOR: _parse_name_selector,
    COMMAND_NAME__TYPE_SELECTOR: _parse_type_selector,
}

ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS = {
    '_SELECTOR_': CONCEPT_NAME.singular,
    '_NAME_SELECTOR_': COMMAND_NAME__NAME_SELECTOR,
    '_TYPE_SELECTOR_': COMMAND_NAME__TYPE_SELECTOR,
    '_PATTERN_': COMMANDS[COMMAND_NAME__NAME_SELECTOR].argument_syntax_element_name,
    '_TYPE_': COMMANDS[COMMAND_NAME__TYPE_SELECTOR].argument_syntax_element_name,
    '_GLOB_PATTERN_': 'Unix glob pattern',
}

_ERR_MSG_FORMAT_STRING_FOR_PARSE_NAME = 'Missing {_PATTERN_} argument for {_NAME_SELECTOR_}'

_SELECTION_DESCRIPTION = """\
Selects a sub set of files in the directory that the test applies to
(instead of applying it to all files in the directory).
"""

_NAME_SELECTOR_SED_DESCRIPTION = """\
Selects files who's name matches the given {_GLOB_PATTERN_}.
"""


def _type_selector_sed_description() -> list:
    return _fnap(_TYPE_SELECTOR_SED_DESCRIPTION) + [_file_types_table()]


_TYPE_SELECTOR_SED_DESCRIPTION = """\
Selects files with the given type. Symbolic links are followed.
{_TYPE_} is one of:
"""

_AND_SELECTOR_SED_DESCRIPTION = """\
Selects files selected by both {_SELECTOR_}s.
"""


def _fnap(s: str) -> list:
    return normalize_and_parse(s.format_map(ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS))


def _file_types_table() -> docs.ParagraphItem:
    def row(type_name: str, description: str) -> list:
        return [
            docs.cell(docs.paras(type_name)),
            docs.cell(_fnap(description)),
        ]

    return docs.first_column_is_header_table([
        row(type_info.type_argument, 'File must be a ' + type_info.description)
        for type_info in sorted(file_properties.TYPE_INFO.values(),
                                key=lambda ti: ti.type_argument)
    ])
