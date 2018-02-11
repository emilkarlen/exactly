"""Functionality for accessing a subset of the files in a directory."""
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, InvokationVariant, \
    cli_argument_syntax_element_description
from exactly_lib.help_texts import doc_format
from exactly_lib.help_texts import expression, instruction_arguments
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.help_texts.entity.types import FILE_MATCHER_TYPE_INFO
from exactly_lib.help_texts.instruction_arguments import MATCHER_ARGUMENT, SELECTION_OPTION, SELECTION
from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.resolver_structure import FileMatcherResolver
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.err_msg.error_info import ErrorMessagePartConstructor
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.expression import parser as ep
from exactly_lib.test_case_utils.file_matcher import file_matchers
from exactly_lib.test_case_utils.file_matcher import resolvers
from exactly_lib.test_case_utils.file_matcher.file_matchers import MATCH_EVERY_FILE
from exactly_lib.test_case_utils.file_matcher.resolvers import FileMatcherConstantResolver
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.parse import parse_reg_ex
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser

SELECTION_OF_ALL_FILES = FileMatcherConstantResolver(MATCH_EVERY_FILE)

NAME_MATCHER_NAME = 'name'

TYPE_MATCHER_NAME = 'type'

NAME_MATCHER_ARGUMENT = instruction_arguments.GLOB_PATTERN

TYPE_MATCHER_ARGUMENT = a.Named('TYPE')

REG_EX_OPTION = a.OptionName(long_name='regex')

REG_EX_ARGUMENT = a.Option(REG_EX_OPTION,
                           syntax_elements.REGEX_SYNTAX_ELEMENT.argument.name)

_TEXT_PARSER = TextParser({
    'MATCHER': syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.singular_name,
})


def selection_syntax_element_description() -> SyntaxElementDescription:
    return cli_argument_syntax_element_description(
        SELECTION,
        _TEXT_PARSER.fnap(_SELECTION_DESCRIPTION),
        [
            InvokationVariant(cl_syntax.arg_syntax(SELECTION_OPTION)),
        ]
    )


class FileSelectionDescriptor(ErrorMessagePartConstructor):
    def __init__(self, resolver: FileMatcherResolver):
        self.resolver = resolver

    def lines(self, environment: InstructionEnvironmentForPostSdsStep) -> list:
        matcher = self.resolver.resolve(environment.symbols)
        line = SELECTION.name.capitalize() + ' : ' + matcher.option_description
        return [line]


def parse_resolver_from_parse_source(source: ParseSource) -> FileMatcherResolver:
    with token_stream_parser.from_parse_source(source) as tp:
        return parse_resolver(tp)


def parse_optional_selection_resolver(parser: TokenParser) -> FileMatcherResolver:
    parser = token_stream_parser.token_parser_with_additional_error_message_format_map(
        parser,
        ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS)
    return parser.consume_and_handle_optional_option(
        SELECTION_OF_ALL_FILES,
        parse_resolver,
        SELECTION_OPTION.name)


def parse_resolver(parser: TokenParser) -> FileMatcherResolver:
    parser = token_stream_parser.token_parser_with_additional_error_message_format_map(
        parser,
        ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS)
    return _parse(parser)


def _parse(parser: TokenParser) -> FileMatcherResolver:
    ret_val = ep.parse(GRAMMAR, parser)
    assert isinstance(ret_val, FileMatcherResolver), ('Must have parsed a ' + str(FileMatcherResolver))
    return ret_val


def _parse_name_matcher(parser: TokenParser) -> FileMatcherResolver:
    return parser.parse_choice_of_optional_option(_parse_name_reg_ex_matcher,
                                                  _parse_name_glob_pattern_matcher,
                                                  REG_EX_OPTION)


def _parse_name_glob_pattern_matcher(parser: TokenParser) -> FileMatcherResolver:
    pattern = parser.consume_mandatory_string_argument(
        _ERR_MSG_FORMAT_STRING_FOR_PARSE_NAME)
    return _constant(file_matchers.FileMatcherNameGlobPattern(pattern))


def _parse_name_reg_ex_matcher(parser: TokenParser) -> FileMatcherResolver:
    compiled_reg_ex = parse_reg_ex.parse_regex(parser)
    return _constant(file_matchers.FileMatcherBaseNameRegExPattern(compiled_reg_ex))


def _parse_type_matcher(parser: TokenParser) -> FileMatcherResolver:
    file_type = parser.consume_mandatory_constant_string_that_must_be_unquoted_and_equal(
        file_properties.SYNTAX_TOKEN_2_FILE_TYPE,
        file_properties.SYNTAX_TOKEN_2_FILE_TYPE.get,
        '{_TYPE_}')
    return _constant(file_matchers.FileMatcherType(file_type))


def _constant(matcher: file_matchers.FileMatcher) -> FileMatcherResolver:
    return FileMatcherConstantResolver(matcher)


ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS = {
    '_MATCHER_': FILE_MATCHER_TYPE_INFO.name.singular,
    '_NAME_MATCHER_': NAME_MATCHER_NAME,
    '_TYPE_MATCHER_': TYPE_MATCHER_NAME,
    '_GLOB_PATTERN_': NAME_MATCHER_ARGUMENT.name,
    '_TYPE_': TYPE_MATCHER_ARGUMENT.name,
    '_SYMLINK_TYPE_': file_properties.TYPE_INFO[FileType.SYMLINK].type_argument,
    '_GLOB_PATTERN_INFORMATIVE_NAME_': syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT.single_line_description_str.lower(),
    '_REG_EX_PATTERN_INFORMATIVE_NAME_': syntax_elements.REGEX_SYNTAX_ELEMENT.single_line_description_str.lower(),
}

_ERR_MSG_FORMAT_STRING_FOR_PARSE_NAME = 'Missing {_GLOB_PATTERN_} argument for {_NAME_MATCHER_}'

_SELECTION_DESCRIPTION = """\
Makes the assertion apply to the sub set of files matched by {MATCHER},
instead of to all files in the directory.
"""

_NAME_MATCHER_SED_DESCRIPTION = """\
Matches files who's ...


  * name : matches {_GLOB_PATTERN_INFORMATIVE_NAME_}, or
  
  
  * base name : matches {_REG_EX_PATTERN_INFORMATIVE_NAME_}
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
            docs.cell(docs.paras(doc_format.enum_name_text(type_name))),
            docs.cell(_fnap(description)),
        ]

    return docs.plain_table([
        row(type_info.type_argument, 'File must be a ' + type_info.description)
        for type_info in sorted(file_properties.TYPE_INFO.values(),
                                key=lambda ti: ti.type_argument)
    ])


NAME_SYNTAX_DESCRIPTION = grammar.SimpleExpressionDescription(
    argument_usage_list=[
        a.Choice(a.Multiplicity.MANDATORY,
                 [
                     instruction_arguments.GLOB_PATTERN,
                     REG_EX_ARGUMENT,
                 ])
    ],
    description_rest=_fnap(_NAME_MATCHER_SED_DESCRIPTION),
    see_also_targets=cross_reference_id_list([
        syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT,
        syntax_elements.REGEX_SYNTAX_ELEMENT,
    ]),
)

TYPE_SYNTAX_DESCRIPTION = grammar.SimpleExpressionDescription(
    argument_usage_list=[
        a.Single(a.Multiplicity.MANDATORY,
                 TYPE_MATCHER_ARGUMENT)],
    description_rest=_type_matcher_sed_description()
)

GRAMMAR = grammar.Grammar(
    concept=grammar.Concept(
        name=FILE_MATCHER_TYPE_INFO.name,
        type_system_type_name=FILE_MATCHER_TYPE_INFO.identifier,
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
