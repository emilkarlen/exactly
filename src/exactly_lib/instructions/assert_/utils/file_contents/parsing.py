from exactly_lib.help_texts import instruction_arguments
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents.instruction_options import EMPTY_ARGUMENT, \
    EQUALS_ARGUMENT, CONTAINS_ARGUMENT
from exactly_lib.instructions.assert_.utils.file_contents.instruction_with_checkers import \
    instruction_with_exist_trans_and_checker, ActualFileChecker
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case_utils.err_msg import diff_msg_utils
from exactly_lib.test_case_utils.err_msg.property_description import PropertyDescriptor
from exactly_lib.test_case_utils.file_transformer import parse_file_transformer
from exactly_lib.test_case_utils.parse import parse_here_doc_or_file_ref
from exactly_lib.test_case_utils.parse.parse_here_doc_or_file_ref import SourceType
from exactly_lib.test_case_utils.parse.reg_ex import compile_regex
from exactly_lib.util.expectation_type import ExpectationType

_OPERATION = 'OPERATION'

EXPECTED_FILE_REL_OPT_ARG_CONFIG = parse_here_doc_or_file_ref.CONFIGURATION

COMPARISON_OPERATOR = 'COMPARISON OPERATOR'


class CheckerParser:
    def __init__(self,
                 description_of_actual_file: PropertyDescriptor,
                 expectation_type: ExpectationType):
        self.description_of_actual_file = description_of_actual_file
        self.expectation_type = expectation_type
        self.parsers = {
            EMPTY_ARGUMENT: self._parse_emptiness_checker,
            EQUALS_ARGUMENT: self._parse_equals_checker,
            CONTAINS_ARGUMENT: self._parse_contains_checker,
        }

    def parse(self, _token_parser: TokenParserPrime) -> ActualFileChecker:
        return _token_parser.parse_mandatory_command(self.parsers, 'Missing contents check argument')

    def _parse_emptiness_checker(self, token_parser: TokenParserPrime) -> ActualFileChecker:
        token_parser.report_superfluous_arguments_if_not_at_eol()
        token_parser.consume_current_line_as_plain_string()
        from exactly_lib.instructions.assert_.utils.file_contents import instruction_for_emptieness
        return instruction_for_emptieness.EmptinessChecker(self.expectation_type,
                                                           self.description_of_actual_file)

    def _parse_equals_checker(self, token_parser: TokenParserPrime) -> ActualFileChecker:
        token_parser.require_is_not_at_eol('Missing ' + instruction_arguments.REG_EX.name)
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

    def _parse_contains_checker(self, token_parser: TokenParserPrime) -> ActualFileChecker:
        token_parser.require_is_not_at_eol('Missing ' + instruction_arguments.REG_EX.name)
        reg_ex_arg = token_parser.consume_mandatory_token('Missing ' + instruction_arguments.REG_EX.name)
        token_parser.report_superfluous_arguments_if_not_at_eol()
        token_parser.consume_current_line_as_plain_string()

        reg_ex = compile_regex(reg_ex_arg.string)

        failure_resolver = diff_msg_utils.DiffFailureInfoResolver(
            self.description_of_actual_file,
            self.expectation_type,
            diff_msg_utils.expected_constant('any line matches {} {}'.format(
                instruction_arguments.REG_EX.name,
                reg_ex_arg.source_string))
        )
        from exactly_lib.instructions.assert_.utils.file_contents import instruction_for_contains
        return instruction_for_contains.checker_for(self.expectation_type, failure_resolver, reg_ex)


def parse_comparison_operation(actual_file: ComparisonActualFile,
                               token_parser: TokenParserPrime) -> AssertPhaseInstruction:
    actual_file_transformer = parse_file_transformer.parse_optional_from_token_parser(token_parser)
    expectation_type = token_parser.consume_optional_negation_operator()
    checker = CheckerParser(actual_file.property_descriptor(), expectation_type).parse(token_parser)
    return instruction_with_exist_trans_and_checker(actual_file,
                                                    actual_file_transformer,
                                                    checker)


def _missing_operator(operators: list):
    msg = 'Missing {}: {}'.format(_OPERATION, '|'.join(operators))
    raise SingleInstructionInvalidArgumentException(msg)


def _ensure_no_more_arguments(source: ParseSource):
    if not source.is_at_eol__except_for_space:
        raise _parse_exception('Superfluous arguments: {}'.format(source.remaining_part_of_current_line))


def _parse_exception(single_line_msg: str) -> SingleInstructionInvalidArgumentException:
    return SingleInstructionInvalidArgumentException(single_line_msg)
