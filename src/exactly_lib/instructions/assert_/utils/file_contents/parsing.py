import re

from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents.instruction_options import NOT_ARGUMENT, EMPTY_ARGUMENT, \
    EQUALS_ARGUMENT, CONTAINS_ARGUMENT
from exactly_lib.instructions.assert_.utils.file_contents.instruction_with_checkers import \
    instruction_with_exist_trans_and_checker, ActualFileChecker
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations import token_parse
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case_utils.err_msg import diff_msg_utils
from exactly_lib.test_case_utils.err_msg.property_description import PropertyDescriptor
from exactly_lib.test_case_utils.file_transformer import parse_file_transformer
from exactly_lib.test_case_utils.parse import parse_here_doc_or_file_ref
from exactly_lib.util.expectation_type import ExpectationType

_OPERATION = 'OPERATION'

EXPECTED_FILE_REL_OPT_ARG_CONFIG = parse_here_doc_or_file_ref.CONFIGURATION

_COMPARISON_OPERATOR = 'COMPARISON OPERATOR'

_REG_EX = 'REG EX'


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
        reg_ex_arg = token_parse.parse_token_on_current_line(source, _REG_EX)
        _ensure_no_more_arguments(source)
        source.consume_current_line()
        try:
            reg_ex = re.compile(reg_ex_arg.string)
        except Exception as ex:
            raise _parse_exception("Invalid {}: '{}'".format(_REG_EX, str(ex)))

        failure_resolver = diff_msg_utils.DiffFailureInfoResolver(
            description_of_actual_file,
            expectation_type,
            diff_msg_utils.expected_constant('any line matches {} {}'.format(_REG_EX, reg_ex_arg.source_string))
        )
        from exactly_lib.instructions.assert_.utils.file_contents import instruction_for_contains
        return instruction_for_contains.checker_for(expectation_type, failure_resolver, reg_ex)

    parsers = {
        EMPTY_ARGUMENT: parse_emptiness_checker,
        EQUALS_ARGUMENT: parse_equals_checker,
        CONTAINS_ARGUMENT: parse_contains_checker,
    }
    peek_source = source.copy
    first_argument = token_parse.parse_plain_token_on_current_line(peek_source, _COMPARISON_OPERATOR).string
    if first_argument in parsers:
        source.catch_up_with(peek_source)
        return parsers[first_argument]()


def parse_comparison_operation(actual_file: ComparisonActualFile,
                               source: ParseSource) -> AssertPhaseInstruction:
    actual_file_transformer = parse_file_transformer.parse_from_parse_source(source)

    def parse_expectation_type() -> ExpectationType:
        peek_source = source.copy
        first_argument = token_parse.parse_plain_token_on_current_line(peek_source, _COMPARISON_OPERATOR).string
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


def _missing_operator(operators: list):
    msg = 'Missing {}: {}'.format(_OPERATION, '|'.join(operators))
    raise SingleInstructionInvalidArgumentException(msg)


def _ensure_no_more_arguments(source: ParseSource):
    if not source.is_at_eol__except_for_space:
        raise _parse_exception('Superfluous arguments: {}'.format(source.remaining_part_of_current_line))


def _parse_exception(single_line_msg: str) -> SingleInstructionInvalidArgumentException:
    return SingleInstructionInvalidArgumentException(single_line_msg)
