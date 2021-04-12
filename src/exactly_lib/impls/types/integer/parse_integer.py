from typing import Optional

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.test_case.instructions import define_symbol as help_texts
from exactly_lib.impls.types.integer import integer_sdv
from exactly_lib.impls.types.integer.integer_ddv import CustomIntegerValidator
from exactly_lib.impls.types.integer.integer_sdv import IntegerSdv
from exactly_lib.impls.types.string_ import parse_string
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, \
    ParserFromTokens
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.reference_restrictions import \
    is_string__all_indirect_refs_are_strings
from exactly_lib.util.messages import expected_found
from exactly_lib.util.str_ import str_constructor


class MandatoryIntegerParser(ParserFromTokens[IntegerSdv]):
    def __init__(self,
                 custom_integer_restriction: Optional[CustomIntegerValidator] = None,
                 integer_argument_name_in_err_msg: str = syntax_elements.INTEGER_SYNTAX_ELEMENT.singular_name,
                 ):
        self._custom_integer_restriction = custom_integer_restriction
        self._integer_argument_name_in_err_msg = integer_argument_name_in_err_msg
        self._string_parser = parse_string.StringFromTokensParser(_STRING_PARSER_CONFIGURATION)

    def parse(self, token_parser: TokenParser) -> IntegerSdv:
        string_sdv = self._string_parser.parse(token_parser)
        return integer_sdv.IntegerSdv(string_sdv,
                                      self._custom_integer_restriction)


def validator_for_non_negative(actual: int) -> Optional[TextRenderer]:
    if actual < 0:
        return expected_found.unexpected_lines(_NON_NEGATIVE_INTEGER_ARGUMENT_DESCRIPTION,
                                               str(actual))
    return None


_NON_NEGATIVE_INTEGER_ARGUMENT_DESCRIPTION = 'An integer >= 0'

_REFERENCE_RESTRICTIONS = is_string__all_indirect_refs_are_strings(
    text_docs.single_pre_formatted_line_object(
        str_constructor.FormatMap(
            'The {INTEGER} argument must be made up of just {string_type} values.',
            {
                'INTEGER': syntax_elements.INTEGER_SYNTAX_ELEMENT.argument.name,
                'string_type': help_texts.ANY_TYPE_INFO_DICT[ValueType.STRING].identifier
            }
        )
    )
)

_STRING_PARSER_CONFIGURATION = parse_string.Configuration(
    syntax_elements.INTEGER_SYNTAX_ELEMENT.singular_name,
    _REFERENCE_RESTRICTIONS,
)
