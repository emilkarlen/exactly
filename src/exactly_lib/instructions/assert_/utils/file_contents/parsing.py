from exactly_lib.help_texts import instruction_arguments
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents.instruction_options import NOT_ARGUMENT, EMPTY_ARGUMENT, \
    EQUALS_ARGUMENT, CONTAINS_ARGUMENT
from exactly_lib.instructions.assert_.utils.file_contents.instruction_with_checkers import \
    instruction_with_exist_trans_and_checker, ActualFileChecker
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations import token_parse
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


def parse_checker(description_of_actual_file: PropertyDescriptor,
                  expectation_type: ExpectationType,
                  source: ParseSource) -> ActualFileChecker:
    def parse_emptiness_checker() -> ActualFileChecker:
        _ensure_no_more_arguments(source)
        source.consume_current_line()
        from exactly_lib.instructions.assert_.utils.file_contents import instruction_for_emptieness
        return instruction_for_emptieness.EmptinessChecker(expectation_type,
                                                           description_of_actual_file)

    def parse_equals_checker() -> ActualFileChecker:
        current_line_before = source.current_line_number
        here_doc_or_file_ref_for_expected = parse_here_doc_or_file_ref.parse_from_parse_source(
            source,
            EXPECTED_FILE_REL_OPT_ARG_CONFIG)
        if source.has_current_line and source.current_line_number == current_line_before:
            _ensure_no_more_arguments(source)
            source.consume_current_line()

        from exactly_lib.instructions.assert_.utils.file_contents import instruction_for_equality
        return instruction_for_equality.EqualityChecker(expectation_type,
                                                        here_doc_or_file_ref_for_expected,
                                                        description_of_actual_file)

    def parse_contains_checker() -> ActualFileChecker:
        reg_ex_arg = token_parse.parse_token_on_current_line(source,
                                                             instruction_arguments.REG_EX.name)
        _ensure_no_more_arguments(source)
        source.consume_current_line()
        reg_ex = compile_regex(reg_ex_arg.string)

        failure_resolver = diff_msg_utils.DiffFailureInfoResolver(
            description_of_actual_file,
            expectation_type,
            diff_msg_utils.expected_constant('any line matches {} {}'.format(
                instruction_arguments.REG_EX.name,
                reg_ex_arg.source_string))
        )
        from exactly_lib.instructions.assert_.utils.file_contents import instruction_for_contains
        return instruction_for_contains.checker_for(expectation_type, failure_resolver, reg_ex)

    parsers = {
        EMPTY_ARGUMENT: parse_emptiness_checker,
        EQUALS_ARGUMENT: parse_equals_checker,
        CONTAINS_ARGUMENT: parse_contains_checker,
    }
    peek_source = source.copy
    first_argument = token_parse.parse_plain_token_on_current_line(peek_source, COMPARISON_OPERATOR).string
    if first_argument in parsers:
        source.catch_up_with(peek_source)
        return parsers[first_argument]()
    else:
        def _no_checker_msg() -> str:
            return '\n'.join([
                'Expecting one of : ' + ', '.join(parsers.keys()),
                'Found            : ' + source.remaining_part_of_current_line,
            ])

        raise SingleInstructionInvalidArgumentException(_no_checker_msg())


def parse_checker_from_token_parser(description_of_actual_file: PropertyDescriptor,
                                    expectation_type: ExpectationType,
                                    _token_parser: TokenParserPrime) -> ActualFileChecker:
    def parse_emptiness_checker(token_parser: TokenParserPrime) -> ActualFileChecker:
        token_parser.report_superfluous_arguments_if_not_at_eol()
        token_parser.consume_current_line_as_plain_string()
        from exactly_lib.instructions.assert_.utils.file_contents import instruction_for_emptieness
        return instruction_for_emptieness.EmptinessChecker(expectation_type,
                                                           description_of_actual_file)

    def parse_equals_checker(token_parser: TokenParserPrime) -> ActualFileChecker:
        token_parser.require_is_not_at_eol('Missing ' + instruction_arguments.REG_EX.name)
        expected_contents = parse_here_doc_or_file_ref.parse_from_token_parser(
            token_parser,
            EXPECTED_FILE_REL_OPT_ARG_CONFIG)
        if expected_contents.source_type is not SourceType.HERE_DOC:
            token_parser.report_superfluous_arguments_if_not_at_eol()
            token_parser.consume_current_line_as_plain_string()

        from exactly_lib.instructions.assert_.utils.file_contents import instruction_for_equality
        return instruction_for_equality.EqualityChecker(expectation_type,
                                                        expected_contents,
                                                        description_of_actual_file)

    def parse_contains_checker(token_parser: TokenParserPrime) -> ActualFileChecker:
        token_parser.require_is_not_at_eol('Missing ' + instruction_arguments.REG_EX.name)
        reg_ex_arg = token_parser.consume_mandatory_token('Missing ' + instruction_arguments.REG_EX.name)
        token_parser.report_superfluous_arguments_if_not_at_eol()
        token_parser.consume_current_line_as_plain_string()

        reg_ex = compile_regex(reg_ex_arg.string)

        failure_resolver = diff_msg_utils.DiffFailureInfoResolver(
            description_of_actual_file,
            expectation_type,
            diff_msg_utils.expected_constant('any line matches {} {}'.format(
                instruction_arguments.REG_EX.name,
                reg_ex_arg.source_string))
        )
        from exactly_lib.instructions.assert_.utils.file_contents import instruction_for_contains
        return instruction_for_contains.checker_for(expectation_type, failure_resolver, reg_ex)

    parsers = {
        EMPTY_ARGUMENT: parse_emptiness_checker,
        EQUALS_ARGUMENT: parse_equals_checker,
        CONTAINS_ARGUMENT: parse_contains_checker,
    }
    return _token_parser.parse_mandatory_command(parsers, 'Missing contents check argument')


def parse_comparison_operation(actual_file: ComparisonActualFile,
                               source: ParseSource) -> AssertPhaseInstruction:
    actual_file_transformer = parse_file_transformer.parse_optional_from_parse_source(source)

    def parse_expectation_type() -> ExpectationType:
        peek_source = source.copy
        first_argument = token_parse.parse_plain_token_on_current_line(peek_source, COMPARISON_OPERATOR).string
        if first_argument == NOT_ARGUMENT:
            source.catch_up_with(peek_source)
            return ExpectationType.NEGATIVE
        else:
            return ExpectationType.POSITIVE

    expectation_type = parse_expectation_type()

    checker = parse_checker(actual_file.property_descriptor(),
                            expectation_type,
                            source)
    return instruction_with_exist_trans_and_checker(actual_file,
                                                    actual_file_transformer,
                                                    checker)


def parse_comparison_operation_from_token_parser(actual_file: ComparisonActualFile,
                                                 token_parser: TokenParserPrime) -> AssertPhaseInstruction:
    actual_file_transformer = parse_file_transformer.parse_optional_from_token_parser(token_parser)
    expectation_type = token_parser.consume_optional_negation_operator()
    checker = parse_checker_from_token_parser(actual_file.property_descriptor(),
                                              expectation_type,
                                              token_parser)
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
