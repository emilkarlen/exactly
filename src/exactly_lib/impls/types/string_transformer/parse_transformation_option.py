from typing import Optional

from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.impls.types.parse.options import OptionalOptionWMandatoryArgumentParser
from exactly_lib.impls.types.string_transformer import parse_string_transformer
from exactly_lib.impls.types.string_transformer.impl.identity import IDENTITY_TRANSFORMER_SDV
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv


def parse_optional_option(token_parser: TokenParser) -> StringTransformerSdv:
    """
    :return: The identity transformer, if transformer option is not given.
    """
    return token_parser.consume_and_handle_optional_option(
        IDENTITY_TRANSFORMER_SDV,
        _PARSER__ANY_LINE__SIMPLE.parse_from_token_parser,
        string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME)


def parse_optional_option__optional(token_parser: TokenParser) -> Optional[StringTransformerSdv]:
    return token_parser.consume_and_handle_optional_option3(
        _PARSER__ANY_LINE__SIMPLE.parse_from_token_parser,
        string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME,
    )


def parser() -> Parser[Optional[StringTransformerSdv]]:
    return OptionalOptionWMandatoryArgumentParser(
        string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME,
        _PARSER__ANY_LINE__SIMPLE,
    )


_PARSER__ANY_LINE__SIMPLE = parse_string_transformer.parsers().simple
