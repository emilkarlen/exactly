"""Functionality for accessing a subset of the files in a directory."""
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, InvokationVariant
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.entity.types import FILE_MATCHER_CONCEPT_INFO
from exactly_lib.help_texts.instruction_arguments import MATCHER_ARGUMENT, SELECTION_OPTION, SELECTION
from exactly_lib.help_texts.type_system import FILE_MATCHER_TYPE
from exactly_lib.named_element.resolver_structure import FileMatcherResolver
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations import token_stream_parse_prime
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.err_msg import property_description
from exactly_lib.test_case_utils.expression import grammar, syntax_documentation
from exactly_lib.test_case_utils.expression import parser as ep
from exactly_lib.test_case_utils.file_matcher import resolvers
from exactly_lib.test_case_utils.file_matcher.file_matchers import SELECT_ALL_FILES, FileMatcherFromSelectors
from exactly_lib.test_case_utils.file_matcher.resolvers import FileMatcherConstantResolver
from exactly_lib.util import dir_contents_selection as dcs
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.dir_contents_selection import Selectors
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs

SELECTION_OF_ALL_FILES = FileMatcherConstantResolver(SELECT_ALL_FILES)

NAME_MATCHER_NAME = 'name'

TYPE_MATCHER_NAME = 'type'

NAME_MATCHER_ARGUMENT = a.Named('PATTERN')

TYPE_MATCHER_ARGUMENT = a.Named('TYPE')

AND_OPERATOR = '&&'


def selection_syntax_element_description() -> SyntaxElementDescription:
    return cl_syntax.cli_argument_syntax_element_description(
        SELECTION,
        docs.paras(_SELECTION_DESCRIPTION),
        [
            InvokationVariant(cl_syntax.arg_syntax(SELECTION_OPTION)),
        ]
    )


def matcher_syntax_element_description() -> SyntaxElementDescription:
    return syntax_documentation.Syntax(GRAMMAR).syntax_element_description()


class SelectorsDescriptor(property_description.ErrorMessagePartConstructor):
    def __init__(self, resolver: FileMatcherResolver):
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
    return dcs.all_files()


def parse_resolver_from_parse_source(source: ParseSource) -> FileMatcherResolver:
    with token_stream_parse_prime.from_parse_source(source) as tp:
        return parse_resolver(tp)


def parse_optional_selection_resolver(parser: TokenParserPrime) -> FileMatcherResolver:
    parser = token_stream_parse_prime.token_parser_with_additional_error_message_format_map(
        parser,
        ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS)
    return parser.consume_and_handle_optional_option(
        SELECTION_OF_ALL_FILES,
        parse_resolver,
        SELECTION_OPTION.name)


def parse_resolver(parser: TokenParserPrime) -> FileMatcherResolver:
    parser = token_stream_parse_prime.token_parser_with_additional_error_message_format_map(
        parser,
        ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS)
    return _parse(parser)


def _parse(parser: TokenParserPrime) -> FileMatcherResolver:
    ret_val = ep.parse(GRAMMAR, parser)
    assert isinstance(ret_val, FileMatcherResolver), ('Must have parsed a ' + str(FileMatcherResolver))
    return ret_val


def _parse_name_matcher(parser: TokenParserPrime) -> FileMatcherResolver:
    pattern = parser.consume_mandatory_string_argument(
        _ERR_MSG_FORMAT_STRING_FOR_PARSE_NAME)
    return _constant(dcs.name_matches_pattern(pattern))


def _parse_type_matcher(parser: TokenParserPrime) -> FileMatcherResolver:
    file_type = parser.consume_mandatory_constant_string_that_must_be_unquoted_and_equal(
        file_properties.SYNTAX_TOKEN_2_FILE_TYPE,
        file_properties.SYNTAX_TOKEN_2_FILE_TYPE.get,
        '{_TYPE_}')
    return _constant(dcs.file_type_is(file_type))


def _constant(selectors: dcs.Selectors) -> FileMatcherResolver:
    return FileMatcherConstantResolver(FileMatcherFromSelectors(selectors))


ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS = {
    '_MATCHER_': FILE_MATCHER_CONCEPT_INFO.name.singular,
    '_NAME_MATCHER_': NAME_MATCHER_NAME,
    '_TYPE_MATCHER_': TYPE_MATCHER_NAME,
    '_PATTERN_': NAME_MATCHER_ARGUMENT.name,
    '_TYPE_': TYPE_MATCHER_ARGUMENT.name,
    '_GLOB_PATTERN_': 'Unix glob pattern',
}

_ERR_MSG_FORMAT_STRING_FOR_PARSE_NAME = 'Missing {_PATTERN_} argument for {_NAME_MATCHER_}'

_SELECTION_DESCRIPTION = """\
Selects a sub set of files in the directory that the test applies to
(instead of applying it to all files in the directory).
"""

_NAME_MATCHER_SED_DESCRIPTION = """\
Selects files who's name matches the given {_GLOB_PATTERN_}.
"""


def _type_matcher_sed_description() -> list:
    return _fnap(_TYPE_MATCHER_SED_DESCRIPTION) + [_file_types_table()]


_TYPE_MATCHER_SED_DESCRIPTION = """\
Selects files with the given type. Symbolic links are followed.
{_TYPE_} is one of:
"""

_AND_MATCHER_SED_DESCRIPTION = """\
Selects files selected by both {_MATCHER_}s.
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


NAME_SYNTAX_DESCRIPTION = grammar.SimpleExpressionDescription(
    argument_usage_list=[
        a.Single(a.Multiplicity.MANDATORY,
                 NAME_MATCHER_ARGUMENT)
    ],
    description_rest=_fnap(_NAME_MATCHER_SED_DESCRIPTION)
)

TYPE_SYNTAX_DESCRIPTION = grammar.SimpleExpressionDescription(
    argument_usage_list=[
        a.Single(a.Multiplicity.MANDATORY,
                 TYPE_MATCHER_ARGUMENT)],
    description_rest=_type_matcher_sed_description()
)

AND_SYNTAX_DESCRIPTION = grammar.OperatorExpressionDescription(
    description_rest=_fnap(_AND_MATCHER_SED_DESCRIPTION)
)

GRAMMAR = grammar.Grammar(
    concept=grammar.Concept(
        name=FILE_MATCHER_CONCEPT_INFO.name,
        type_system_type_name=FILE_MATCHER_TYPE,
        syntax_element_name=MATCHER_ARGUMENT,
    ),
    mk_reference=resolvers.FileMatcherReferenceResolver,
    simple_expressions={
        NAME_MATCHER_NAME: grammar.SimpleExpression(_parse_name_matcher,
                                                    NAME_SYNTAX_DESCRIPTION),
        TYPE_MATCHER_NAME: grammar.SimpleExpression(_parse_type_matcher,
                                                    TYPE_SYNTAX_DESCRIPTION),
    },
    complex_expressions={
        AND_OPERATOR: grammar.ComplexExpression(resolvers.FileMatcherAndResolver,
                                                AND_SYNTAX_DESCRIPTION),
    }
)
