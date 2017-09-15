from exactly_lib.help_texts import instruction_arguments
from exactly_lib.instructions.assert_.utils.assertion_part import SequenceOfCooperativeAssertionParts, \
    AssertionPart
from exactly_lib.instructions.assert_.utils.expression import parse as parse_cmp_op
from exactly_lib.instructions.assert_.utils.expression.parse import validator_for_non_negative
from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.instructions.assert_.utils.file_contents.parts.contents_checkers import FileTransformerAsAssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.parts.file_assertion_part import ActualFileAssertionPart
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime, \
    token_parser_with_additional_error_message_format_map
from exactly_lib.test_case_utils.lines_transformer import parse_lines_transformer
from exactly_lib.test_case_utils.parse import parse_here_doc_or_file_ref
from exactly_lib.test_case_utils.parse.parse_here_doc_or_file_ref import SourceType
from exactly_lib.test_case_utils.parse.reg_ex import compile_regex
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.messages import grammar_options_syntax


def parse(token_parser: TokenParserPrime) -> AssertionPart:
    """
    :return: A :class:`AssertionPart` that takes an FileToCheck as (last) argument.
    """
    actual_lines_transformer = parse_lines_transformer.parse_optional_transformer_resolver(token_parser)
    expectation_type = token_parser.consume_optional_negation_operator()
    parser_of_contents_assertion_part = ParseFileContentsAssertionPart(expectation_type)
    file_contents_assertion_part = parser_of_contents_assertion_part.parse(token_parser)
    return SequenceOfCooperativeAssertionParts([FileTransformerAsAssertionPart(actual_lines_transformer),
                                                file_contents_assertion_part])


_OPERATION = 'OPERATION'

EXPECTED_FILE_REL_OPT_ARG_CONFIG = parse_here_doc_or_file_ref.CONFIGURATION

COMPARISON_OPERATOR = 'COMPARISON OPERATOR'

_FORMAT_MAP = {
    '_REGEX_': instruction_arguments.REG_EX.name,
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

    def parse(self, token_parser: TokenParserPrime) -> ActualFileAssertionPart:
        token_parser = token_parser_with_additional_error_message_format_map(token_parser, _FORMAT_MAP)
        return token_parser.parse_mandatory_command(self.parsers, 'Missing {_CHECK_}')

    def _parse_emptiness_checker(self, token_parser: TokenParserPrime) -> ActualFileAssertionPart:
        token_parser.report_superfluous_arguments_if_not_at_eol()
        token_parser.consume_current_line_as_plain_string()
        from exactly_lib.instructions.assert_.utils.file_contents.parts import emptieness
        return emptieness.EmptinessAssertionPart(self.expectation_type)

    def _parse_equals_checker(self, token_parser: TokenParserPrime) -> ActualFileAssertionPart:
        token_parser.require_is_not_at_eol(parse_here_doc_or_file_ref.MISSING_SOURCE)
        expected_contents = parse_here_doc_or_file_ref.parse_from_token_parser(
            token_parser,
            EXPECTED_FILE_REL_OPT_ARG_CONFIG)
        if expected_contents.source_type is not SourceType.HERE_DOC:
            token_parser.report_superfluous_arguments_if_not_at_eol()
            token_parser.consume_current_line_as_plain_string()

        from exactly_lib.instructions.assert_.utils.file_contents.parts import equality
        return equality.EqualityAssertionPart(
            self.expectation_type,
            expected_contents,
        )

    def _parse_any_line_matches_checker(self, token_parser: TokenParserPrime) -> ActualFileAssertionPart:
        reg_ex_arg, reg_ex = self._parse_line_matches_tokens_and_regex(token_parser)

        from exactly_lib.instructions.assert_.utils.file_contents.parts import line_matches
        return line_matches.assertion_part_for_any_line_matches(self.expectation_type,
                                                                reg_ex,
                                                                reg_ex_arg.source_string)

    def _parse_every_line_matches_checker(self, token_parser: TokenParserPrime) -> ActualFileAssertionPart:
        reg_ex_arg, reg_ex = self._parse_line_matches_tokens_and_regex(token_parser)

        from exactly_lib.instructions.assert_.utils.file_contents.parts import line_matches
        return line_matches.assertion_part_for_every_line_matches(self.expectation_type,
                                                                  reg_ex,
                                                                  reg_ex_arg.source_string)

    def _parse_num_lines_checker(self, token_parser: TokenParserPrime) -> ActualFileAssertionPart:
        cmp_op_and_rhs = parse_cmp_op.parse_integer_comparison_operator_and_rhs(token_parser,
                                                                                validator_for_non_negative)
        token_parser.report_superfluous_arguments_if_not_at_eol()
        token_parser.consume_current_line_as_plain_string()
        from exactly_lib.instructions.assert_.utils.file_contents.parts.num_lines import \
            assertion_part_for_num_lines
        return assertion_part_for_num_lines(self.expectation_type,
                                            cmp_op_and_rhs)

    @staticmethod
    def _parse_line_matches_tokens_and_regex(token_parser: TokenParserPrime):
        token_parser.consume_mandatory_constant_unquoted_string(instruction_options.LINE_ARGUMENT,
                                                                must_be_on_current_line=True)
        token_parser.consume_mandatory_constant_unquoted_string(instruction_options.MATCHES_ARGUMENT,
                                                                must_be_on_current_line=True)
        token_parser.require_is_not_at_eol('Missing {_REGEX_}')
        reg_ex_arg = token_parser.consume_mandatory_token('Missing {_REGEX_}')
        token_parser.report_superfluous_arguments_if_not_at_eol()
        token_parser.consume_current_line_as_plain_string()

        return reg_ex_arg, compile_regex(reg_ex_arg.string)
