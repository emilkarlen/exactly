from exactly_lib.definitions import instruction_arguments
from exactly_lib.instructions.assert_.utils import assertion_part
from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.instructions.assert_.utils.file_contents.parts.contents_checkers import FileTransformerAsAssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.parts.file_assertion_part import FileContentsAssertionPart
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, \
    token_parser_with_additional_error_message_format_map
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.messages import grammar_options_syntax


def parse(token_parser: TokenParser) -> AssertionPart:
    """
    :return: A :class:`AssertionPart` that takes an ResolvedComparisonActualFile as (last) argument.
    """

    actual_lines_transformer = parse_string_transformer.parse_optional_transformer_resolver_preceding_mandatory_element(
        token_parser,
        COMPARISON_OPERATOR,
    )
    expectation_type = token_parser.consume_optional_negation_operator()
    file_contents_assertion_part = ParseFileContentsAssertionPart(expectation_type).parse(token_parser)
    return assertion_part.compose(FileTransformerAsAssertionPart(actual_lines_transformer),
                                  file_contents_assertion_part)


_OPERATION = 'OPERATION'

COMPARISON_OPERATOR = 'COMPARISON OPERATOR'

_FORMAT_MAP = {
    '_MATCHER_': instruction_arguments.LINE_MATCHER.name,
    '_CHECK_': '{} ({})'.format(COMPARISON_OPERATOR,
                                grammar_options_syntax.alternatives_list(instruction_options.ALL_CHECKS)),
}


class ParseFileContentsAssertionPart:
    def __init__(self, expectation_type: ExpectationType):
        self.expectation_type = expectation_type
        self.parsers = {
            instruction_options.EMPTY_ARGUMENT: self._parse_emptiness_checker,
            instruction_options.EQUALS_ARGUMENT: self._parse_equals_checker,
            instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT: self._parse_any_line_matches_checker,
            instruction_arguments.ALL_QUANTIFIER_ARGUMENT: self._parse_every_line_matches_checker,
            instruction_options.NUM_LINES_ARGUMENT: self._parse_num_lines_checker,
        }

    def parse(self, token_parser: TokenParser) -> FileContentsAssertionPart:
        token_parser = token_parser_with_additional_error_message_format_map(token_parser, _FORMAT_MAP)
        return token_parser.parse_mandatory_command(self.parsers, _FORMAT_MAP['_CHECK_'])

    def _parse_emptiness_checker(self, token_parser: TokenParser) -> FileContentsAssertionPart:
        from exactly_lib.instructions.assert_.utils.file_contents.parts import emptieness
        return emptieness.parse(self.expectation_type, token_parser)

    def _parse_equals_checker(self, token_parser: TokenParser) -> FileContentsAssertionPart:
        from exactly_lib.instructions.assert_.utils.file_contents.parts import equality
        return equality.parse(self.expectation_type, token_parser)

    def _parse_num_lines_checker(self, token_parser: TokenParser) -> FileContentsAssertionPart:
        from exactly_lib.instructions.assert_.utils.file_contents.parts import num_lines
        return num_lines.parse(self.expectation_type, token_parser)

    def _parse_any_line_matches_checker(self, token_parser: TokenParser) -> FileContentsAssertionPart:
        from exactly_lib.instructions.assert_.utils.file_contents.parts import line_matches
        return line_matches.parse_any_line_matches_checker(self.expectation_type, token_parser)

    def _parse_every_line_matches_checker(self, token_parser: TokenParser) -> FileContentsAssertionPart:
        from exactly_lib.instructions.assert_.utils.file_contents.parts import line_matches
        return line_matches.parse_every_line_matches_checker(self.expectation_type, token_parser)
