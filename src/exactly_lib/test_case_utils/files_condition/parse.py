from typing import Optional, Tuple, Sequence

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.definitions.entity import syntax_elements, types
from exactly_lib.section_document.element_parsers.error_messages import MessageFactory
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import ParserWithCurrentLineVariants
from exactly_lib.symbol.data.restrictions.reference_restrictions import string_made_up_by_just_strings
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.expression import parser as grammar_parser
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.files_condition import files_conditions
from exactly_lib.test_case_utils.files_condition import syntax
from exactly_lib.test_case_utils.files_condition.structure import FilesConditionSdv
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.type_system.logic.file_matcher import FileMatcherSdv
from exactly_lib.util import strings
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import Token
from . import documentation


def parser() -> ParserWithCurrentLineVariants[FilesConditionSdv]:
    return _PARSER


class _Parser(ParserWithCurrentLineVariants[FilesConditionSdv]):
    def __init__(self):
        super().__init__(consume_last_line_if_is_at_eol_after_parse=True)

    def parse_from_token_parser(self,
                                tokens: TokenParser,
                                must_be_on_current_line: bool = False) -> FilesConditionSdv:
        return parse(tokens, must_be_on_current_line)


def parse(tokens: TokenParser,
          must_be_on_current_line: bool = True) -> FilesConditionSdv:
    return grammar_parser.parse(GRAMMAR, tokens, must_be_on_current_line)


def _parse_constant(tokens: TokenParser) -> FilesConditionSdv:
    elements = _parse_elements(tokens)

    tokens.require_has_valid_head_token(_FILE_NAME_OR_SET_END)

    tokens.consume_mandatory_keyword__part_of_syntax_element(
        syntax.END_BRACE,
        False,
        syntax_elements.FILES_CONDITION_SYNTAX_ELEMENT.singular_name,
    )

    return files_conditions.new_constant(elements)


def _parse_elements(tokens: TokenParser) -> Sequence[Tuple[StringSdv, Optional[FileMatcherSdv]]]:
    _multiple_files_per_line_error = _MESSAGE_FACTORY.generator_for(_MULTIPLE_FILES_ON_SINGLE_LINE)

    def is_at_eol_or_end_of_set():
        if tokens.is_at_eol:
            return
        else:
            tokens.require_head_is_unquoted_and_equals(syntax.END_BRACE, _multiple_files_per_line_error)

    def parse_element() -> Tuple[StringSdv, Optional[FileMatcherSdv]]:
        file_name = parse_string.parse_string_sdv(tokens.token_stream, _FILE_NAME_STRING_CONFIGURATION)
        if tokens.head_is_unquoted_and_equals(syntax.FILE_MATCHER_SEPARATOR):
            tokens.consume_head()
            file_matcher = parse_file_matcher.parse_sdv(tokens, False)
            return file_name, file_matcher
        else:
            is_at_eol_or_end_of_set()
            return file_name, None

    ret_val = []
    while tokens.has_valid_head_token() and not _token_is_set_end(tokens.head):
        ret_val.append(parse_element())

    return ret_val


def _token_is_set_end(token: Token) -> bool:
    return token.is_plain and token.string == syntax.END_BRACE


def _token_is_matcher_separator(token: Token) -> bool:
    return token.is_plain and token.string == syntax.FILE_MATCHER_SEPARATOR


_PARSER = _Parser()

_FILE_NAME_STRING_REFERENCES_RESTRICTION = string_made_up_by_just_strings(
    text_docs.single_pre_formatted_line_object(
        strings.FormatMap(
            'A file name must be defined in terms of {string_type}.',
            {'string_type': syntax_elements.STRING_SYNTAX_ELEMENT.singular_name},
        )
    )
)

_FILE_NAME_STRING_CONFIGURATION = parse_string.Configuration(
    'FILE-NAME',
    _FILE_NAME_STRING_REFERENCES_RESTRICTION,
)

_MESSAGE_FACTORY = MessageFactory({
    'FILES_CONDITION': syntax_elements.FILES_CONDITION_SYNTAX_ELEMENT.singular_name,
})

_FILE_NAME_OR_SET_END = 'FILE-NAME or ' + syntax.END_BRACE__FOR_FORMAT_STRINGS
_HEADER = """\
Reading {FILES_CONDITION}"""

_MULTIPLE_FILES_ON_SINGLE_LINE = """\
There can only be one file per line.
"""

GRAMMAR = grammar.Grammar(
    concept=grammar.Concept(
        name=types.FILES_CONDITION_TYPE_INFO.name,
        type_system_type_name=types.FILES_CONDITION_TYPE_INFO.identifier,
        syntax_element_name=syntax_elements.FILES_CONDITION_SYNTAX_ELEMENT.argument,
    ),
    mk_reference=files_conditions.new_reference,
    primitive_expressions=(
        NameAndValue(
            syntax.BEGIN_BRACE,
            grammar.PrimitiveExpression(_parse_constant,
                                        documentation.ConstantSyntaxDescription())

        ),
    ),
    infix_op_expressions=(),
    prefix_op_expressions=(),
)
