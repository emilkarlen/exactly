from typing import Optional

from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import types, syntax_elements
from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.test_case_utils.expression import grammar, parser as parse_expression
from exactly_lib.test_case_utils.string_transformer import names
from exactly_lib.test_case_utils.string_transformer import sdvs
from exactly_lib.test_case_utils.string_transformer.impl import filter, replace, sequence, identity
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser

IDENTITY_TRANSFORMER_SDV = sdvs.StringTransformerSdvConstant(identity.IdentityStringTransformer())

REPLACE_REGEX_ARGUMENT = instruction_arguments.REG_EX

STRING_TRANSFORMER_ARGUMENT = a.Named(types.STRING_TRANSFORMER_TYPE_INFO.syntax_element_name)


def parser() -> Parser[StringTransformerSdv]:
    return _PARSER


class _Parser(Parser[StringTransformerSdv]):
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
    return token_parser.consume_and_handle_optional_option2(
        parse_string_transformer_from_token_parser,
        IDENTITY_TRANSFORMER_SDV,
        instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME)


def parse_optional_transformer_sdv2(token_parser: TokenParser) -> Optional[StringTransformerSdv]:
    """
    :return: The identity transformer, if transformer option is not given.
    """
    return token_parser.consume_and_handle_optional_option3(
        parse_string_transformer_from_token_parser,
        instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME)


def parse_optional_transformer_sdv_preceding_mandatory_element(parser: TokenParser,
                                                               mandatory_element_name: str
                                                               ) -> Optional[StringTransformerSdv]:
    parser.require_existing_valid_head_token(mandatory_element_name)
    return parse_optional_transformer_sdv2(parser)


def parse_string_transformer_from_token_parser(parser: TokenParser) -> StringTransformerSdv:
    return parse_expression.parse(GRAMMAR, parser)


ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS = {
    '_REG_EX_': REPLACE_REGEX_ARGUMENT.name,
    '_STRING_': replace.REPLACE_REPLACEMENT_ARGUMENT.name,
    '_TRANSFORMER_': types.STRING_TRANSFORMER_TYPE_INFO.name.singular,
    '_LINE_MATCHER_': types.LINE_MATCHER_TYPE_INFO.name.singular,
    '_TRANSFORMERS_': types.STRING_TRANSFORMER_TYPE_INFO.name.plural,
}

_TEXT_PARSER = TextParser(ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS)

_REPLACE_TRANSFORMER_SED_DESCRIPTION = """\
Replaces parts of the contents of a file.


Every occurrence of regular expression {_REG_EX_} - on a single line - is replaced with {_STRING_}.


Backslash escapes in {_STRING_} are processed.
That is, \\n is converted to a single newline character, \\r is converted to a carriage return, and so forth.


Unknown escapes such as \\& are left alone.


Back-references, such as \\6, are replaced with the substring matched by group 6 in {_REG_EX_}.
"""

_SELECT_TRANSFORMER_SED_DESCRIPTION = """\
Keeps lines matched by the given {_LINE_MATCHER_},
and discards lines not matched."""

_SEQUENCE_TRANSFORMER_SED_DESCRIPTION = """\
Sequence of two or more {_TRANSFORMERS_}.

The result of the {_TRANSFORMER_} to the left is feed to the
{_TRANSFORMER_} to the right.
"""

_REPLACE_SYNTAX_DESCRIPTION = grammar.SimpleExpressionDescription(
    argument_usage_list=[
        a.Single(a.Multiplicity.MANDATORY,
                 REPLACE_REGEX_ARGUMENT),
        a.Single(a.Multiplicity.MANDATORY,
                 replace.REPLACE_REPLACEMENT_ARGUMENT),
    ],
    description_rest=_TEXT_PARSER.fnap(_REPLACE_TRANSFORMER_SED_DESCRIPTION),
    see_also_targets=[syntax_elements.REGEX_SYNTAX_ELEMENT.cross_reference_target],
)

_SELECT_SYNTAX_DESCRIPTION = grammar.SimpleExpressionDescription(
    argument_usage_list=[
        a.Single(a.Multiplicity.MANDATORY,
                 instruction_arguments.LINE_MATCHER),
    ],
    description_rest=_TEXT_PARSER.fnap(_SELECT_TRANSFORMER_SED_DESCRIPTION),
    see_also_targets=[types.LINE_MATCHER_TYPE_INFO.cross_reference_target],
)

_SEQUENCE_SYNTAX_DESCRIPTION = grammar.OperatorExpressionDescription(
    _TEXT_PARSER.fnap(_SEQUENCE_TRANSFORMER_SED_DESCRIPTION)
)

_CONCEPT = grammar.Concept(
    types.STRING_TRANSFORMER_TYPE_INFO.name,
    types.STRING_TRANSFORMER_TYPE_INFO.identifier,
    STRING_TRANSFORMER_ARGUMENT,
)


def _mk_reference(name: str) -> StringTransformerSdv:
    return sdvs.StringTransformerSdvReference(name)


GRAMMAR = grammar.Grammar(
    _CONCEPT,
    mk_reference=_mk_reference,
    simple_expressions={
        names.REPLACE_TRANSFORMER_NAME:
            grammar.SimpleExpression(replace.parse_replace,
                                     _REPLACE_SYNTAX_DESCRIPTION),
        names.SELECT_TRANSFORMER_NAME:
            grammar.SimpleExpression(filter.parse_filter,
                                     _SELECT_SYNTAX_DESCRIPTION),
    },
    complex_expressions={
        names.SEQUENCE_OPERATOR_NAME: grammar.ComplexExpression(
            sequence.StringTransformerSequenceSdv,
            _SEQUENCE_SYNTAX_DESCRIPTION,
        ),
    },
    prefix_expressions={},
)
