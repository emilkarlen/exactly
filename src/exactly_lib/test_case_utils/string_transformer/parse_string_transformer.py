from typing import Optional

from exactly_lib.definitions.entity import types, syntax_elements
from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import Parser, ParserFromTokenParserBase
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.test_case_utils.expression import grammar, parser as parse_expression
from exactly_lib.test_case_utils.string_transformer import names
from exactly_lib.test_case_utils.string_transformer import sdvs
from exactly_lib.test_case_utils.string_transformer.impl import filter, replace, sequence, identity
from exactly_lib.test_case_utils.string_transformer.impl.identity import IDENTITY_TRANSFORMER_SDV
from exactly_lib.test_case_utils.string_transformer.impl.run_program import parse as parse_run
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name_and_value import NameAndValue

STRING_TRANSFORMER_ARGUMENT = a.Named(types.STRING_TRANSFORMER_TYPE_INFO.syntax_element_name)


def parser() -> Parser[StringTransformerSdv]:
    return _PARSER


class _Parser(ParserFromTokenParserBase[StringTransformerSdv]):
    def __init__(self):
        super().__init__(consume_last_line_if_is_at_eol_after_parse=False)

    def parse_from_token_parser(self, parser: TokenParser) -> StringTransformerSdv:
        return parse_string_transformer_from_token_parser(parser)


_PARSER = _Parser()


def parse_string_transformer(source: ParseSource) -> StringTransformerSdv:
    with token_stream_parser.from_parse_source(source) as tp:
        return parse_optional_transformer_sdv(tp)


def parse_optional_transformer_sdv(token_parser: TokenParser) -> StringTransformerSdv:
    """
    :return: The identity transformer, if transformer option is not given.
    """
    return token_parser.consume_and_handle_optional_option(
        IDENTITY_TRANSFORMER_SDV,
        parse_string_transformer_from_token_parser,
        string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME)


def parse_optional_transformer_sdv2(token_parser: TokenParser) -> Optional[StringTransformerSdv]:
    """
    :return: The identity transformer, if transformer option is not given.
    """
    return token_parser.consume_and_handle_optional_option3(
        parse_string_transformer_from_token_parser,
        string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME)


def parse_optional_transformer_sdv_preceding_mandatory_element(parser: TokenParser,
                                                               mandatory_element_name: str
                                                               ) -> Optional[StringTransformerSdv]:
    parser.require_existing_valid_head_token(mandatory_element_name)
    return parse_optional_transformer_sdv2(parser)


def parse_string_transformer_from_token_parser(parser: TokenParser,
                                               must_be_on_current_line: bool = True) -> StringTransformerSdv:
    return parse_expression.parse(GRAMMAR, parser, must_be_on_current_line)


_CONCEPT = grammar.Concept(
    types.STRING_TRANSFORMER_TYPE_INFO.name,
    types.STRING_TRANSFORMER_TYPE_INFO.identifier,
    syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.argument,
)


def _mk_reference(name: str) -> StringTransformerSdv:
    return sdvs.StringTransformerSdvReference(name)


GRAMMAR = grammar.Grammar(
    _CONCEPT,
    mk_reference=_mk_reference,
    primitive_expressions=(
        NameAndValue(
            names.REPLACE_TRANSFORMER_NAME,
            grammar.PrimitiveExpression(replace.parse_replace,
                                        replace.SyntaxDescription())
        ),
        NameAndValue(
            names.SELECT_TRANSFORMER_NAME,
            grammar.PrimitiveExpression(filter.parse_filter,
                                        filter.SyntaxDescription())
        ),
        NameAndValue(
            names.RUN_PROGRAM_TRANSFORMER_NAME,
            grammar.PrimitiveExpression(parse_run.parse,
                                        parse_run.SyntaxDescription())
        ),
        NameAndValue(
            names.IDENTITY_TRANSFORMER_NAME,
            grammar.PrimitiveExpression(identity.parse_identity,
                                        identity.SyntaxDescription())
        ),
    ),
    infix_op_expressions=[
        NameAndValue(
            names.SEQUENCE_OPERATOR_NAME,
            grammar.InfixOpExpression(
                sequence.StringTransformerSequenceSdv,
                sequence.SYNTAX_DESCRIPTION,
            )
        ),
    ],
    prefix_op_expressions=(),
)
