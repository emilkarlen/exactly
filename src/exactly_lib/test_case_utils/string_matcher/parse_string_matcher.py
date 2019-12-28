from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import concepts
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, \
    token_parser_with_additional_error_message_format_map
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol import symbol_syntax
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case_utils.matcher.impls import combinator_sdvs
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.test_case_utils.string_matcher.impl import sdvs
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer
from exactly_lib.type_system.logic.string_matcher import FileToCheck
from exactly_lib.util.logic_types import ExpectationType, Quantifier

COMPARISON_OPERATOR = 'COMPARISON OPERATOR'
_FORMAT_MAP = {
    '_MATCHER_': instruction_arguments.LINE_MATCHER.name,
}


def string_matcher_parser() -> Parser[StringMatcherSdv]:
    return parser_classes.ParserFromTokenParserFunction(parse_string_matcher,
                                                        consume_last_line_if_is_at_eol_after_parse=False)


def parse_string_matcher(parser: TokenParser) -> StringMatcherSdv:
    return StringMatcherSdv(parse_string_matcher__generic(parser))


def parse_string_matcher__generic(parser: TokenParser) -> MatcherSdv[FileToCheck]:
    mb_model_transformer = parse_string_transformer.parse_optional_transformer_sdv_preceding_mandatory_element(
        parser,
        COMPARISON_OPERATOR,
    )
    expectation_type = parser.consume_optional_negation_operator()
    matcher_except_transformation = _StringMatcherParser().parse(parser)
    if expectation_type is ExpectationType.NEGATIVE:
        matcher_except_transformation = combinator_sdvs.Negation(matcher_except_transformation)
    return (
        sdvs.new_with_transformation__generic(mb_model_transformer, matcher_except_transformation)
        if mb_model_transformer
        else
        matcher_except_transformation
    )


class _StringMatcherParser:
    def __init__(self):
        self.parsers = {
            matcher_options.EMPTY_ARGUMENT: self._parse_emptiness_checker,
            matcher_options.EQUALS_ARGUMENT: self._parse_equals_checker,
            matcher_options.MATCHES_ARGUMENT: self._parse_matches_checker,
            instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT: self._parse_any_line_matches_checker,
            instruction_arguments.ALL_QUANTIFIER_ARGUMENT: self._parse_every_line_matches_checker,
            matcher_options.NUM_LINES_ARGUMENT: self._parse_num_lines_checker,
        }

    def parse(self, token_parser: TokenParser) -> MatcherSdv[FileToCheck]:
        token_parser = token_parser_with_additional_error_message_format_map(token_parser, _FORMAT_MAP)
        matcher_name = token_parser.consume_mandatory_unquoted_string(
            instruction_arguments.STRING_MATCHER_PRIMITIVE_SYNTAX_ELEMENT,
            False)
        if matcher_name in self.parsers:
            return self.parsers[matcher_name](token_parser)
        else:
            return self._symbol_reference(matcher_name, token_parser)

    def _parse_emptiness_checker(self, token_parser: TokenParser) -> MatcherSdv[FileToCheck]:
        from exactly_lib.test_case_utils.string_matcher.parse.parts import emptieness
        return emptieness.parse__generic(token_parser)

    def _parse_equals_checker(self, token_parser: TokenParser) -> MatcherSdv[FileToCheck]:
        from exactly_lib.test_case_utils.string_matcher.parse.parts import equality
        return equality.parse__generic(token_parser)

    def _parse_matches_checker(self, token_parser: TokenParser) -> MatcherSdv[FileToCheck]:
        from exactly_lib.test_case_utils.string_matcher.parse.parts import matches
        return matches.parse__generic(token_parser)

    def _parse_num_lines_checker(self, token_parser: TokenParser) -> MatcherSdv[FileToCheck]:
        from exactly_lib.test_case_utils.string_matcher.parse.parts import num_lines
        return num_lines.parse__generic(token_parser)

    def _parse_any_line_matches_checker(self, token_parser: TokenParser) -> MatcherSdv[FileToCheck]:
        from exactly_lib.test_case_utils.string_matcher.parse.parts import line_matches
        return line_matches.parse__generic(Quantifier.EXISTS, token_parser)

    def _parse_every_line_matches_checker(self, token_parser: TokenParser) -> MatcherSdv[FileToCheck]:
        from exactly_lib.test_case_utils.string_matcher.parse.parts import line_matches
        return line_matches.parse__generic(Quantifier.ALL, token_parser)

    def _symbol_reference(self, parsed_symbol_name: str, token_parser: TokenParser) -> MatcherSdv[FileToCheck]:
        if symbol_syntax.is_symbol_name(parsed_symbol_name):
            return sdvs.new_reference__generic(parsed_symbol_name, ExpectationType.POSITIVE)
        else:
            err_msg_header = 'Neither a {matcher} nor the plain name of a {symbol}: '.format(
                matcher=instruction_arguments.STRING_MATCHER_PRIMITIVE_SYNTAX_ELEMENT,
                symbol=concepts.SYMBOL_CONCEPT_INFO.singular_name)
            raise SingleInstructionInvalidArgumentException(err_msg_header + parsed_symbol_name)
