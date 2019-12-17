from exactly_lib.definitions import instruction_arguments
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.test_case_utils.matcher.impls import quantifier_matchers
from exactly_lib.test_case_utils.matcher.impls.quantifier_matchers import MODEL, ELEMENT
from exactly_lib.util.logic_types import Quantifier


def parse_after_quantifier_token(
        quantifier: Quantifier,
        element_predicate_parser: parser_classes.Parser[MatcherSdv[ELEMENT]],
        setup: quantifier_matchers.ElementSetup[MODEL, ELEMENT],
        token_parser: TokenParser,
) -> MatcherSdv[MODEL]:
    token_parser.consume_mandatory_constant_unquoted_string(
        setup.rendering.type_name,
        must_be_on_current_line=True)
    token_parser.consume_mandatory_constant_unquoted_string(
        instruction_arguments.QUANTIFICATION_SEPARATOR_ARGUMENT,
        must_be_on_current_line=True)

    element_predicate = element_predicate_parser.parse_from_token_parser(token_parser)

    return quantifier_matchers.sdv(setup, quantifier, element_predicate)
