from exactly_lib.help_texts import instruction_arguments
from exactly_lib.instructions.assert_.utils.expression import parse as parse_cmp_op
from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents.instruction_with_checkers import \
    instruction_with_exist_trans_and_checker, ActualFileChecker
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime, \
    token_parser_with_additional_error_message_format_map
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case_utils.err_msg import diff_msg_utils
from exactly_lib.test_case_utils.err_msg import property_description
from exactly_lib.test_case_utils.err_msg.property_description import PropertyDescriptor
from exactly_lib.test_case_utils.file_transformer import parse_file_transformer
from exactly_lib.test_case_utils.file_transformer.file_transformer import FileTransformerResolver
from exactly_lib.test_case_utils.parse import parse_here_doc_or_file_ref
from exactly_lib.test_case_utils.parse.parse_here_doc_or_file_ref import SourceType
from exactly_lib.test_case_utils.parse.reg_ex import compile_regex
from exactly_lib.util.expectation_type import ExpectationType
from exactly_lib.util.messages import expected_found
from exactly_lib.util.messages import grammar_options_syntax


def parse_comparison_operation(actual_file: ComparisonActualFile,
                               token_parser: TokenParserPrime) -> AssertPhaseInstruction:
    actual_file_transformer = parse_file_transformer.parse_optional_from_token_parser(token_parser)
    expectation_type = token_parser.consume_optional_negation_operator()
    checker = CheckerParser(actual_file.property_descriptor(), expectation_type, actual_file_transformer).parse(
        token_parser)
    return instruction_with_exist_trans_and_checker(actual_file,
                                                    actual_file_transformer,
                                                    checker)


_OPERATION = 'OPERATION'

EXPECTED_FILE_REL_OPT_ARG_CONFIG = parse_here_doc_or_file_ref.CONFIGURATION

COMPARISON_OPERATOR = 'COMPARISON OPERATOR'

_FORMAT_MAP = {
    '_REGEX_': instruction_arguments.REG_EX.name,
    '_CHECK_': '{} ({})'.format(COMPARISON_OPERATOR,
                                grammar_options_syntax.alternatives_list(instruction_options.ALL_CHECKS)),
}


class CheckerParser:
    def __init__(self,
                 description_of_actual_file: PropertyDescriptor,
                 expectation_type: ExpectationType,
                 actual_file_transformer_resolver: FileTransformerResolver):
        self.expectation_type = expectation_type
        self.description_of_actual_file = description_of_actual_file
        self.file_transformer_resolver = actual_file_transformer_resolver
        self.parsers = {
            instruction_options.EMPTY_ARGUMENT: self._parse_emptiness_checker,
            instruction_options.EQUALS_ARGUMENT: self._parse_equals_checker,
            instruction_options.ANY_LINE_ARGUMENT: self._parse_any_line_matches_checker,
            instruction_options.EVERY_LINE_ARGUMENT: self._parse_every_line_matches_checker,
            instruction_options.NUM_LINES_ARGUMENT: self._parse_num_lines_checker,
        }

    def parse(self, token_parser: TokenParserPrime) -> ActualFileChecker:
        token_parser = token_parser_with_additional_error_message_format_map(token_parser, _FORMAT_MAP)
        return token_parser.parse_mandatory_command(self.parsers, 'Missing {_CHECK_}')

    def _parse_emptiness_checker(self, token_parser: TokenParserPrime) -> ActualFileChecker:
        token_parser.report_superfluous_arguments_if_not_at_eol()
        token_parser.consume_current_line_as_plain_string()
        from exactly_lib.instructions.assert_.utils.file_contents import instruction_for_emptieness
        return instruction_for_emptieness.EmptinessChecker(self.expectation_type,
                                                           self.description_of_actual_file)

    def _parse_equals_checker(self, token_parser: TokenParserPrime) -> ActualFileChecker:
        token_parser.require_is_not_at_eol(parse_here_doc_or_file_ref.MISSING_SOURCE)
        expected_contents = parse_here_doc_or_file_ref.parse_from_token_parser(
            token_parser,
            EXPECTED_FILE_REL_OPT_ARG_CONFIG)
        if expected_contents.source_type is not SourceType.HERE_DOC:
            token_parser.report_superfluous_arguments_if_not_at_eol()
            token_parser.consume_current_line_as_plain_string()

        from exactly_lib.instructions.assert_.utils.file_contents import instruction_for_equality
        return instruction_for_equality.EqualityChecker(self.expectation_type,
                                                        expected_contents,
                                                        self.description_of_actual_file)

    def _parse_any_line_matches_checker(self, token_parser: TokenParserPrime) -> ActualFileChecker:
        reg_ex_arg, reg_ex = self._parse_line_matches_tokens_and_regex(token_parser)

        failure_resolver = self._diff_failure_info_resolver_for_line_matches(instruction_options.ANY_LINE_ARGUMENT,
                                                                             reg_ex_arg.source_string)
        from exactly_lib.instructions.assert_.utils.file_contents import instruction_for_contains
        return instruction_for_contains.checker_for_any_line_matches(self.expectation_type, failure_resolver, reg_ex)

    def _parse_every_line_matches_checker(self, token_parser: TokenParserPrime) -> ActualFileChecker:
        reg_ex_arg, reg_ex = self._parse_line_matches_tokens_and_regex(token_parser)

        failure_resolver = self._diff_failure_info_resolver_for_line_matches(instruction_options.EVERY_LINE_ARGUMENT,
                                                                             reg_ex_arg.source_string)
        from exactly_lib.instructions.assert_.utils.file_contents import instruction_for_contains
        return instruction_for_contains.checker_for_every_line_matches(self.expectation_type, failure_resolver, reg_ex)

    def _parse_num_lines_checker(self, token_parser: TokenParserPrime) -> ActualFileChecker:
        cmp_op_and_rhs = parse_cmp_op.parse_integer_comparison_operator_and_rhs(token_parser,
                                                                                _must_be_non_negative_integer)
        token_parser.report_superfluous_arguments_if_not_at_eol()
        token_parser.consume_current_line_as_plain_string()
        from exactly_lib.instructions.assert_.utils.file_contents.instruction_for_num_lines import checker_for_num_lines
        return checker_for_num_lines(self.expectation_type,
                                     cmp_op_and_rhs,
                                     self._actual_file_property_descriptor(instruction_options.NUM_LINES_DESCRIPTION))

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

    def _diff_failure_info_resolver_for_line_matches(self,
                                                     any_or_every_keyword: str,
                                                     reg_ex_arg: str) -> diff_msg_utils.DiffFailureInfoResolver:
        return diff_msg_utils.DiffFailureInfoResolver(
            self.description_of_actual_file,
            self.expectation_type,
            diff_msg_utils.expected_constant(' '.join([
                any_or_every_keyword,
                instruction_options.LINE_ARGUMENT,
                instruction_options.MATCHES_ARGUMENT,
                instruction_arguments.REG_EX.name,
                reg_ex_arg])
            ))

    def _actual_file_property_descriptor(self, property_name: str) -> property_description.PropertyDescriptor:
        return property_description.PropertyDescriptorWithConstantPropertyName(
            property_name,
            property_description.multiple_object_descriptors([
                self.description_of_actual_file,
                parse_file_transformer.FileTransformerDescriptor(self.file_transformer_resolver),
            ])
        )


def _must_be_non_negative_integer(actual: int) -> str:
    if actual < 0:
        return expected_found.unexpected_lines('an integer >= 0',
                                               str(actual))
    return None
