"""Functionality for accessing a subset of the files in a directory."""
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, InvokationVariant
from exactly_lib.help_texts import expression
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
from exactly_lib.test_case_utils.file_matcher import file_matchers
from exactly_lib.test_case_utils.file_matcher import resolvers
from exactly_lib.test_case_utils.file_matcher.file_matchers import MATCH_EVERY_FILE
from exactly_lib.test_case_utils.file_matcher.resolvers import FileMatcherConstantResolver
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs

SELECTION_OF_ALL_FILES = FileMatcherConstantResolver(MATCH_EVERY_FILE)

NAME_MATCHER_NAME = 'name'

TYPE_MATCHER_NAME = 'type'

NAME_MATCHER_ARGUMENT = a.Named('PATTERN')

TYPE_MATCHER_ARGUMENT = a.Named('TYPE')


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


class FileSelectionDescriptor(property_description.ErrorMessagePartConstructor):
    def __init__(self, resolver: FileMatcherResolver):
        self.resolver = resolver

    def lines(self, environment: InstructionEnvironmentForPostSdsStep) -> list:
        matcher = self.resolver.resolve(environment.symbols)
        line = SELECTION.name.capitalize() + ' : ' + matcher.option_description
        return [line]


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
    return _constant(file_matchers.FileMatcherNameGlobPattern(pattern))


def _parse_type_matcher(parser: TokenParserPrime) -> FileMatcherResolver:
    file_type = parser.consume_mandatory_constant_string_that_must_be_unquoted_and_equal(
        file_properties.SYNTAX_TOKEN_2_FILE_TYPE,
        file_properties.SYNTAX_TOKEN_2_FILE_TYPE.get,
        '{_TYPE_}')
    return _constant(file_matchers.FileMatcherType(file_type))


def _constant(matcher: file_matchers.FileMatcher) -> FileMatcherResolver:
    return FileMatcherConstantResolver(matcher)


ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS = {
    '_MATCHER_': FILE_MATCHER_CONCEPT_INFO.name.singular,
    '_NAME_MATCHER_': NAME_MATCHER_NAME,
    '_TYPE_MATCHER_': TYPE_MATCHER_NAME,
    '_PATTERN_': NAME_MATCHER_ARGUMENT.name,
    '_TYPE_': TYPE_MATCHER_ARGUMENT.name,
    '_SYMLINK_TYPE_': file_properties.TYPE_INFO[FileType.SYMLINK].type_argument,
    '_GLOB_PATTERN_': 'Unix glob pattern',
}

_ERR_MSG_FORMAT_STRING_FOR_PARSE_NAME = 'Missing {_PATTERN_} argument for {_NAME_MATCHER_}'

_SELECTION_DESCRIPTION = """\
Selects a sub set of files in the directory that the test applies to
(instead of applying it to all files in the directory).
"""

_NAME_MATCHER_SED_DESCRIPTION = """\
Matches files who's name matches the given {_GLOB_PATTERN_}.
"""


def _type_matcher_sed_description() -> list:
    return _fnap(_TYPE_MATCHER_SED_DESCRIPTION) + [_file_types_table()]


_TYPE_MATCHER_SED_DESCRIPTION = """\
Matches files with the given type. Symbolic links are followed (unless matched type is {_SYMLINK_TYPE_}).
{_TYPE_} is one of:
"""

_NOT_SED_DESCRIPTION = """\
Matches files not matched by the given matcher.
"""

_AND_SED_DESCRIPTION = """\
Matches files matched by all matchers.
"""

_OR_SED_DESCRIPTION = """\
Matches files matched by any matcher.
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
        expression.AND_OPERATOR_NAME:
            grammar.ComplexExpression(resolvers.FileMatcherAndResolver,
                                      grammar.OperatorExpressionDescription(
                                          _fnap(_AND_SED_DESCRIPTION)
                                      )),
        expression.OR_OPERATOR_NAME:
            grammar.ComplexExpression(resolvers.FileMatcherOrResolver,
                                      grammar.OperatorExpressionDescription(
                                          _fnap(_OR_SED_DESCRIPTION)
                                      )),
    },
    prefix_expressions={
        expression.NOT_OPERATOR_NAME:
            grammar.PrefixExpression(resolvers.FileMatcherNotResolver,
                                     grammar.OperatorExpressionDescription(
                                         _fnap(_NOT_SED_DESCRIPTION)
                                     ))
    },
)
