from exactly_lib.definitions import instruction_arguments
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, \
    token_parser_with_additional_error_message_format_map
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.resolver_structure import StringMatcherResolver
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.messages import grammar_options_syntax

COMPARISON_OPERATOR = 'COMPARISON OPERATOR'
_FORMAT_MAP = {
    '_MATCHER_': instruction_arguments.LINE_MATCHER.name,
    '_CHECK_': '{} ({})'.format(COMPARISON_OPERATOR,
                                grammar_options_syntax.alternatives_list(matcher_options.ALL_CHECKS)),
}


def string_matcher_parser() -> Parser[StringMatcherResolver]:
    return parser_classes.ParserFromTokenParserFunction(parse_string_matcher)


def parse_string_matcher(parser: TokenParser) -> StringMatcherResolver:
    expectation_type = parser.consume_optional_negation_operator()
    return StringMatcherParser(expectation_type).parse(parser)


class StringMatcherParser:
    def __init__(self, expectation_type: ExpectationType):
        self.expectation_type = expectation_type
        self.parsers = {
            matcher_options.EMPTY_ARGUMENT: self._parse_emptiness_checker,
            matcher_options.EQUALS_ARGUMENT: self._parse_equals_checker,
            instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT: self._parse_any_line_matches_checker,
            instruction_arguments.ALL_QUANTIFIER_ARGUMENT: self._parse_every_line_matches_checker,
            matcher_options.NUM_LINES_ARGUMENT: self._parse_num_lines_checker,
        }

    def parse(self, token_parser: TokenParser) -> StringMatcherResolver:
        token_parser = token_parser_with_additional_error_message_format_map(token_parser, _FORMAT_MAP)
        return token_parser.parse_mandatory_command(self.parsers, _FORMAT_MAP['_CHECK_'])

    def _parse_emptiness_checker(self, token_parser: TokenParser) -> StringMatcherResolver:
        from exactly_lib.test_case_utils.string_matcher.parse.parts import emptieness
        return emptieness.parse(self.expectation_type, token_parser)

    def _parse_equals_checker(self, token_parser: TokenParser) -> StringMatcherResolver:
        from exactly_lib.test_case_utils.string_matcher.parse.parts import equality
        return equality.parse(self.expectation_type, token_parser)

    def _parse_num_lines_checker(self, token_parser: TokenParser) -> StringMatcherResolver:
        from exactly_lib.test_case_utils.string_matcher.parse.parts import num_lines
        return num_lines.parse(self.expectation_type, token_parser)

    def _parse_any_line_matches_checker(self, token_parser: TokenParser) -> StringMatcherResolver:
        from exactly_lib.test_case_utils.string_matcher.parse.parts import line_matches
        return line_matches.parse_any_line_matches_matcher(self.expectation_type, token_parser)

    def _parse_every_line_matches_checker(self, token_parser: TokenParser) -> StringMatcherResolver:
        from exactly_lib.test_case_utils.string_matcher.parse.parts import line_matches
        return line_matches.parse_every_line_matches_matcher(self.expectation_type, token_parser)
