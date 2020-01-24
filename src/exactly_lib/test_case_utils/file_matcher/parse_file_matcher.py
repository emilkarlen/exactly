from typing import List, Optional, Sequence

from exactly_lib.definitions import doc_format, matcher_model
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.entity.types import FILE_MATCHER_TYPE_INFO
from exactly_lib.definitions.instruction_arguments import MATCHER_ARGUMENT, SELECTION_OPTION
from exactly_lib.definitions.primitives.file_matcher import NAME_MATCHER_NAME, TYPE_MATCHER_NAME
from exactly_lib.definitions.test_case.file_check_properties import REGULAR_FILE_CONTENTS, DIR_CONTENTS
from exactly_lib.processing import exit_values
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.file_matcher import FileMatcherSdv
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.expression import parser as ep
from exactly_lib.test_case_utils.file_matcher import file_matchers
from exactly_lib.test_case_utils.file_matcher.impl import \
    name_regex, name_glob_pattern, regular_file_contents, dir_contents, file_contents_utils
from exactly_lib.test_case_utils.file_matcher.impl.file_type import FileMatcherType
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.matcher import standard_expression_grammar
from exactly_lib.test_case_utils.matcher.impls import sdv_components
from exactly_lib.test_case_utils.string_matcher import parse_string_matcher
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel, GenericFileMatcherSdv
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel
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
        return parse_sdv(parser)


class ParserOfGenericMatcherOnArbitraryLine(parser_classes.Parser[MatcherSdv[FileMatcherModel]]):
    def parse_from_token_parser(self, token_parser: TokenParser) -> GenericFileMatcherSdv:
        return _parse__generic(token_parser, must_be_on_current_line=False)


_PARSER = _Parser()


def parse_optional_selection_sdv(parser: TokenParser) -> Optional[FileMatcherSdv]:
    parser = token_stream_parser.token_parser_with_additional_error_message_format_map(
        parser,
        ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS)
    return parser.consume_and_handle_optional_option(
        None,
        parse_sdv,
        SELECTION_OPTION.name)


def parse_sdv(parser: TokenParser,
              must_be_on_current_line: bool = True) -> FileMatcherSdv:
    generic_matcher = _parse__generic(parser, must_be_on_current_line)
    return FileMatcherSdv(generic_matcher)


def _parse__generic(parser: TokenParser,
                    must_be_on_current_line: bool) -> GenericFileMatcherSdv:
    parser = token_stream_parser.token_parser_with_additional_error_message_format_map(
        parser,
        ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS)
    return ep.parse(GRAMMAR, parser, must_be_on_current_line)


def _parse_name_matcher(parser: TokenParser) -> GenericFileMatcherSdv:
    return parser.parse_choice_of_optional_option(name_regex.parse__generic,
                                                  name_glob_pattern.parse__generic,
                                                  REG_EX_OPTION)


def _parse_type_matcher(parser: TokenParser) -> GenericFileMatcherSdv:
    file_type = parser.consume_mandatory_constant_string_that_must_be_unquoted_and_equal(
        file_properties.SYNTAX_TOKEN_2_FILE_TYPE,
        file_properties.SYNTAX_TOKEN_2_FILE_TYPE.get,
        '{_TYPE_}')
    return sdv_components.matcher_sdv_from_constant_primitive(FileMatcherType(file_type))


def _parse_regular_file_contents(parser: TokenParser) -> GenericFileMatcherSdv:
    string_matcher = parse_string_matcher.parse_string_matcher__generic(parser,
                                                                        must_be_on_current_line=False)
    return regular_file_contents.sdv__generic(string_matcher)


def _parse_dir_contents(token_parser: TokenParser) -> GenericFileMatcherSdv:
    return token_parser.parse_choice_of_optional_option(
        _parse_dir_contents__recursive,
        _parse_dir_contents__non_recursive,
        instruction_arguments.RECURSIVE_OPTION.name,
    )


def _parse_dir_contents__non_recursive(token_parser: TokenParser) -> GenericFileMatcherSdv:
    return _parse_dir_contents__for_setup(dir_contents.SETUP__NON_RECURSIVE, token_parser)


def _parse_dir_contents__recursive(token_parser: TokenParser) -> GenericFileMatcherSdv:
    return _parse_dir_contents__for_setup(dir_contents.SETUP__RECURSIVE, token_parser)


def _parse_dir_contents__for_setup(setup: file_contents_utils.Setup[FilesMatcherModel],
                                   token_parser: TokenParser,
                                   ) -> GenericFileMatcherSdv:
    from exactly_lib.test_case_utils.files_matcher import parse_files_matcher
    files_matcher = parse_files_matcher.parse_files_matcher__generic(token_parser)
    return dir_contents.dir_matches_files_matcher_sdv__generic(setup,
                                                               files_matcher)


def _constant(matcher: file_matchers.FileMatcher) -> GenericFileMatcherSdv:
    return sdv_components.matcher_sdv_from_constant_primitive(matcher)


ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS = {
    '_MATCHER_': FILE_MATCHER_TYPE_INFO.name.singular,
    '_NAME_MATCHER_': NAME_MATCHER_NAME,
    '_TYPE_MATCHER_': TYPE_MATCHER_NAME,
    '_GLOB_PATTERN_': NAME_MATCHER_ARGUMENT.name,
    '_TYPE_': TYPE_MATCHER_ARGUMENT.name,
    '_SYMLINK_TYPE_': file_properties.TYPE_INFO[FileType.SYMLINK].type_argument,
    'HARD_ERROR': exit_values.EXECUTION__HARD_ERROR.exit_identifier,
    '_GLOB_PATTERN_INFORMATIVE_NAME_': syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT.single_line_description_str.lower(),
    '_REG_EX_PATTERN_INFORMATIVE_NAME_': syntax_elements.REGEX_SYNTAX_ELEMENT.single_line_description_str.lower(),
    'MODEL': matcher_model.FILE_MATCHER_MODEL,
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


class _NameSyntaxDescription(grammar.SimpleExpressionDescription):
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


class _TypeSyntaxDescription(grammar.SimpleExpressionDescription):
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
        name=FILE_MATCHER_TYPE_INFO.name,
        type_system_type_name=FILE_MATCHER_TYPE_INFO.identifier,
        syntax_element_name=MATCHER_ARGUMENT,
    ),
    model=matcher_model.FILE_MATCHER_MODEL,
    value_type=ValueType.FILE_MATCHER,
    simple_expressions=(
        NameAndValue(
            NAME_MATCHER_NAME,
            grammar.SimpleExpression(_parse_name_matcher,
                                     _NameSyntaxDescription())
        ),

        NameAndValue(
            TYPE_MATCHER_NAME,
            grammar.SimpleExpression(_parse_type_matcher,
                                     _TypeSyntaxDescription())
        ),

        NameAndValue(
            REGULAR_FILE_CONTENTS,
            grammar.SimpleExpression(
                _parse_regular_file_contents,
                file_contents_utils.FileContentsSyntaxDescription(regular_file_contents.SETUP)
            )
        ),

        NameAndValue(
            DIR_CONTENTS,
            grammar.SimpleExpression(
                _parse_dir_contents,
                file_contents_utils.FileContentsSyntaxDescription(dir_contents.SETUP__NON_RECURSIVE)
            )
        ),
    ),
)

_ERR_MSG_FORMAT_STRING_FOR_PARSE_NAME = 'Missing {_GLOB_PATTERN_} argument for {_NAME_MATCHER_}'

_NAME_MATCHER_SED_DESCRIPTION = """\
Matches {MODEL:s} who's ...


  * name : matches {_GLOB_PATTERN_INFORMATIVE_NAME_}, or
  
  
  * base name : matches {_REG_EX_PATTERN_INFORMATIVE_NAME_}
"""


def _type_matcher_sed_description() -> List[docs.ParagraphItem]:
    return _TP.fnap(_TYPE_MATCHER_SED_DESCRIPTION) + [_file_types_table()]


_TYPE_MATCHER_SED_DESCRIPTION = """\
Matches {MODEL:s} with the given type. Symbolic links are followed (unless matched type is {_SYMLINK_TYPE_}).
{_TYPE_} is one of:
"""

_TP = TextParser(ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS)
