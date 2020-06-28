from typing import List, Sequence

from exactly_lib.definitions import doc_format, matcher_model, misc_texts
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements, types
from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.definitions.primitives.file_matcher import NAME_MATCHER_NAME, TYPE_MATCHER_NAME
from exactly_lib.definitions.test_case.file_check_properties import REGULAR_FILE_CONTENTS, DIR_CONTENTS
from exactly_lib.processing import exit_values
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.expression import parser as ep
from exactly_lib.test_case_utils.file_matcher import parse_dir_contents_model, file_or_dir_contents_doc
from exactly_lib.test_case_utils.file_matcher.impl import \
    name_regex, name_glob_pattern, regular_file_contents, dir_contents, file_contents_utils
from exactly_lib.test_case_utils.file_matcher.impl.file_type import FileMatcherType
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.matcher import standard_expression_grammar
from exactly_lib.test_case_utils.matcher.impls import sdv_components
from exactly_lib.test_case_utils.string_matcher import parse_string_matcher
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel, FileMatcherSdv, FileMatcher
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser

NAME_MATCHER_ARGUMENT = instruction_arguments.GLOB_PATTERN

TYPE_MATCHER_ARGUMENT = a.Named('TYPE')

REG_EX_OPTION = a.OptionName(long_name='regex')

REG_EX_ARGUMENT = a.Option(REG_EX_OPTION,
                           syntax_elements.REGEX_SYNTAX_ELEMENT.argument.name)


def parser() -> parser_classes.Parser[FileMatcherSdv]:
    return _PARSER


class _Parser(parser_classes.Parser[FileMatcherSdv]):
    def parse_from_token_parser(self, parser: TokenParser) -> FileMatcherSdv:
        return parse_sdv(parser, must_be_on_current_line=True)


class ParserOfMatcherOnArbitraryLine(parser_classes.Parser[MatcherSdv[FileMatcherModel]]):
    def parse_from_token_parser(self, token_parser: TokenParser) -> FileMatcherSdv:
        return parse_sdv(token_parser, must_be_on_current_line=False)


_PARSER = _Parser()


def parse_sdv(parser: TokenParser,
              must_be_on_current_line: bool) -> FileMatcherSdv:
    parser = token_stream_parser.token_parser_with_additional_error_message_format_map(
        parser,
        ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS)
    return ep.parse(GRAMMAR, parser, must_be_on_current_line)


def _parse_name_matcher(parser: TokenParser) -> FileMatcherSdv:
    return parser.parse_choice_of_optional_option(name_regex.parse,
                                                  name_glob_pattern.parse,
                                                  REG_EX_OPTION)


def _parse_type_matcher(parser: TokenParser) -> FileMatcherSdv:
    file_type = parser.consume_mandatory_constant_string_that_must_be_unquoted_and_equal(
        file_properties.SYNTAX_TOKEN_2_FILE_TYPE,
        file_properties.SYNTAX_TOKEN_2_FILE_TYPE.get,
        '{_TYPE_}')
    return sdv_components.matcher_sdv_from_constant_primitive(FileMatcherType(file_type))


def _parse_regular_file_contents(parser: TokenParser) -> FileMatcherSdv:
    string_matcher = parse_string_matcher.parse_string_matcher(parser,
                                                               must_be_on_current_line=False)
    return regular_file_contents.sdv(string_matcher)


def _parse_dir_contents(token_parser: TokenParser) -> FileMatcherSdv:
    from exactly_lib.test_case_utils.files_matcher import parse_files_matcher
    model_constructor = DIR_CONTENTS_MODEL_PARSER.parse(token_parser)
    files_matcher = parse_files_matcher.parse_files_matcher(token_parser,
                                                            False)
    return dir_contents.dir_matches_files_matcher_sdv(model_constructor,
                                                      files_matcher)


def _constant(matcher: FileMatcher) -> FileMatcherSdv:
    return sdv_components.matcher_sdv_from_constant_primitive(matcher)


ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS = {
    '_MATCHER_': types.FILE_MATCHER_TYPE_INFO.name.singular,
    '_NAME_MATCHER_': NAME_MATCHER_NAME,
    '_TYPE_MATCHER_': TYPE_MATCHER_NAME,
    '_GLOB_PATTERN_': NAME_MATCHER_ARGUMENT.name,
    '_TYPE_': TYPE_MATCHER_ARGUMENT.name,
    '_SYMLINK_TYPE_': file_properties.TYPE_INFO[FileType.SYMLINK].type_argument,
    'HARD_ERROR': exit_values.EXECUTION__HARD_ERROR.exit_identifier,
    '_GLOB_PATTERN_INFORMATIVE_NAME_': syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT.single_line_description_str.lower(),
    '_REG_EX_PATTERN_INFORMATIVE_NAME_': syntax_elements.REGEX_SYNTAX_ELEMENT.single_line_description_str.lower(),
    'MODEL': matcher_model.FILE_MATCHER_MODEL,
    'SYMBOLIC_LINKS_ARE_FOLLOWED': misc_texts.SYMBOLIC_LINKS_ARE_FOLLOWED,
}


def _file_types_table() -> docs.ParagraphItem:
    def row(type_name: str, description: str) -> list:
        return [
            docs.cell(docs.paras(doc_format.enum_name_text(type_name))),
            docs.cell(_TP.fnap(description)),
        ]

    return docs.plain_table([
        row(type_info.type_argument, 'File must be a ' + type_info.description)
        for type_info in sorted(file_properties.TYPE_INFO.values(),
                                key=lambda ti: ti.type_argument)
    ])


class _NameSyntaxDescription(grammar.PrimitiveExpressionDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            a.Choice(a.Multiplicity.MANDATORY,
                     [
                         instruction_arguments.GLOB_PATTERN,
                         REG_EX_ARGUMENT,
                     ])
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_NAME_MATCHER_SED_DESCRIPTION)

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return cross_reference_id_list([
            syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT,
            syntax_elements.REGEX_SYNTAX_ELEMENT,
        ])


class _TypeSyntaxDescription(grammar.PrimitiveExpressionDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            a.Single(a.Multiplicity.MANDATORY,
                     TYPE_MATCHER_ARGUMENT)
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _type_matcher_sed_description()


GRAMMAR = standard_expression_grammar.new_grammar(
    concept=grammar.Concept(
        name=types.FILE_MATCHER_TYPE_INFO.name,
        type_system_type_name=types.FILE_MATCHER_TYPE_INFO.identifier,
        syntax_element_name=syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.argument,
    ),
    model=matcher_model.FILE_MATCHER_MODEL,
    value_type=ValueType.FILE_MATCHER,
    simple_expressions=(
        NameAndValue(
            NAME_MATCHER_NAME,
            grammar.PrimitiveExpression(_parse_name_matcher,
                                        _NameSyntaxDescription())
        ),

        NameAndValue(
            TYPE_MATCHER_NAME,
            grammar.PrimitiveExpression(_parse_type_matcher,
                                        _TypeSyntaxDescription())
        ),

        NameAndValue(
            REGULAR_FILE_CONTENTS,
            grammar.PrimitiveExpression(
                _parse_regular_file_contents,
                file_contents_utils.FileContentsSyntaxDescription(
                    file_or_dir_contents_doc.REGULAR_FILE_DOCUMENTATION_SETUP
                )
            )
        ),

        NameAndValue(
            DIR_CONTENTS,
            grammar.PrimitiveExpression(
                _parse_dir_contents,
                file_contents_utils.FileContentsSyntaxDescription(
                    file_or_dir_contents_doc.DIR_DOCUMENTATION
                )
            )
        ),
    ),
)

_ERR_MSG_FORMAT_STRING_FOR_PARSE_NAME = 'Missing {_GLOB_PATTERN_} argument for {_NAME_MATCHER_}'

_DIR_CONTENTS_MODEL_NOT_ON_CURRENT_LINE_ERR_MSG = token_stream_parser.ErrorMessageConfiguration(
    'Missing {_CONTENTS_OPTIONS_} or {_FILES_MATCHER_}',
    {
        '_CONTENTS_OPTIONS_': file_or_dir_contents.DIR_FILE_SET_OPTIONS.name,
        '_FILES_MATCHER_': syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.singular_name,
    }
)

DIR_CONTENTS_MODEL_PARSER = parse_dir_contents_model.Parser(_DIR_CONTENTS_MODEL_NOT_ON_CURRENT_LINE_ERR_MSG)

_NAME_MATCHER_SED_DESCRIPTION = """\
Matches {MODEL:s} who's ...


  * name : matches {_GLOB_PATTERN_INFORMATIVE_NAME_}, or
  
  
  * base name : matches {_REG_EX_PATTERN_INFORMATIVE_NAME_}
"""


def _type_matcher_sed_description() -> List[docs.ParagraphItem]:
    return _TP.fnap(_TYPE_MATCHER_SED_DESCRIPTION) + [_file_types_table()]


_TYPE_MATCHER_SED_DESCRIPTION = """\
Matches {MODEL:s} with the given type. {SYMBOLIC_LINKS_ARE_FOLLOWED} (unless matched type is {_SYMLINK_TYPE_}).
{_TYPE_} is one of:
"""

_TP = TextParser(ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS)
