import re

from exactly_lib.instructions.assert_.utils.file_contents import actual_file_transformers
from exactly_lib.instructions.assert_.utils.file_contents.actual_file_transformers import ActualFileTransformer
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents.instruction_options import WITH_REPLACED_ENV_VARS_OPTION_NAME, \
    NOT_ARGUMENT, EMPTY_ARGUMENT, EQUALS_ARGUMENT, CONTAINS_ARGUMENT
from exactly_lib.instructions.utils.err_msg import diff_msg_utils
from exactly_lib.instructions.utils.expectation_type import from_is_negated
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations import token_parse
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case_utils.parse import parse_here_doc_or_file_ref
from exactly_lib.util.cli_syntax.option_parsing import matches
from exactly_lib.util.parse.token import TokenType

_OPERATION = 'OPERATION'

EXPECTED_FILE_REL_OPT_ARG_CONFIG = parse_here_doc_or_file_ref.CONFIGURATION

_COMPARISON_OPERATOR = 'COMPARISON OPERATOR'

_REG_EX = 'REG EX'


def parse_comparison_operation(actual_file: ComparisonActualFile,
                               actual_file_transformer_for_replace_env_vars: ActualFileTransformer,
                               source: ParseSource) -> AssertPhaseInstruction:
    def _parse_empty(negated: bool,
                     actual: ComparisonActualFile) -> AssertPhaseInstruction:
        _ensure_no_more_arguments(source)
        source.consume_current_line()
        from exactly_lib.instructions.assert_.utils.file_contents.instruction_for_emptieness import \
            EmptinessAssertionInstruction
        return EmptinessAssertionInstruction(not negated, actual)

    def _parse_equals(negated: bool,
                      actual_file_transformer: ActualFileTransformer,
                      actual: ComparisonActualFile) -> AssertPhaseInstruction:
        current_line_before = source.current_line_number
        here_doc_or_file_ref_for_expected = parse_here_doc_or_file_ref.parse_from_parse_source(
            source,
            EXPECTED_FILE_REL_OPT_ARG_CONFIG)
        if source.has_current_line and source.current_line_number == current_line_before:
            _ensure_no_more_arguments(source)
            source.consume_current_line()

        from exactly_lib.instructions.assert_.utils.file_contents.instruction_for_equality import \
            EqualsAssertionInstruction
        return EqualsAssertionInstruction(negated,
                                          here_doc_or_file_ref_for_expected,
                                          actual,
                                          actual_file_transformer)

    def _parse_contains(negated: bool,
                        actual_file_transformer: ActualFileTransformer,
                        actual: ComparisonActualFile) -> AssertPhaseInstruction:
        reg_ex_arg = token_parse.parse_token_on_current_line(source, _REG_EX)
        _ensure_no_more_arguments(source)
        source.consume_current_line()
        try:
            reg_ex = re.compile(reg_ex_arg.string)
        except Exception as ex:
            raise _parse_exception("Invalid {}: '{}'".format(_REG_EX, str(ex)))

        expectation_type = from_is_negated(negated)
        failure_resolver = diff_msg_utils.DiffFailureInfoResolver(
            actual.property_descriptor(),
            expectation_type,
            diff_msg_utils.expected_constant('any line matches {} {}'.format(_REG_EX, reg_ex_arg.source_string))
        )
        from exactly_lib.instructions.assert_.utils.file_contents import instruction_for_contains

        if negated:
            file_checker = instruction_for_contains.FileCheckerForNegativeMatch(failure_resolver, reg_ex)
        else:
            file_checker = instruction_for_contains.FileCheckerForPositiveMatch(failure_resolver, reg_ex)
        return instruction_for_contains.ContainsAssertionInstruction(file_checker, actual, actual_file_transformer)

    def _parse_contents(actual: ComparisonActualFile) -> AssertPhaseInstruction:
        with_replaced_env_vars = False
        peek_source = source.copy
        next_arg = token_parse.parse_token_or_none_on_current_line(peek_source)
        if next_arg is not None and next_arg.type == TokenType.PLAIN and \
                matches(WITH_REPLACED_ENV_VARS_OPTION_NAME, next_arg.string):
            source.catch_up_with(peek_source)
            with_replaced_env_vars = True
        actual_file_transformer = actual_file_transformers.IdentityFileTransformer()
        if with_replaced_env_vars:
            actual_file_transformer = actual_file_transformer_for_replace_env_vars
        if source.is_at_eol__except_for_space:
            return _missing_operator([NOT_ARGUMENT, EQUALS_ARGUMENT, CONTAINS_ARGUMENT])
        negated = False
        next_arg_str = token_parse.parse_plain_token_on_current_line(source).string
        if next_arg_str == NOT_ARGUMENT:
            negated = True
            if source.is_at_eol__except_for_space:
                return _missing_operator([EQUALS_ARGUMENT, CONTAINS_ARGUMENT])
            next_arg_str = token_parse.parse_plain_token_on_current_line(source, _OPERATION).string
        if next_arg_str == CONTAINS_ARGUMENT:
            return _parse_contains(negated, actual_file_transformer, actual)
        if next_arg_str == EQUALS_ARGUMENT:
            return _parse_equals(negated, actual_file_transformer, actual)
        raise _parse_exception('Unknown {}: {}'.format(_OPERATION, next_arg_str))

    peek_source = source.copy
    first_argument = token_parse.parse_plain_token_on_current_line(peek_source, _COMPARISON_OPERATOR).string
    if first_argument == EMPTY_ARGUMENT:
        source.catch_up_with(peek_source)
        return _parse_empty(False, actual_file)
    second_argument = token_parse.parse_token_on_current_line(peek_source, _COMPARISON_OPERATOR)
    if second_argument.is_plain and [first_argument, second_argument.string] == [NOT_ARGUMENT, EMPTY_ARGUMENT]:
        source.catch_up_with(peek_source)
        return _parse_empty(True, actual_file)
    else:
        return _parse_contents(actual_file)


def _missing_operator(operators: list):
    msg = 'Missing {}: {}'.format(_OPERATION, '|'.join(operators))
    raise SingleInstructionInvalidArgumentException(msg)


def _ensure_no_more_arguments(source: ParseSource):
    if not source.is_at_eol__except_for_space:
        raise _parse_exception('Superfluous arguments: {}'.format(source.remaining_part_of_current_line))


def _parse_exception(single_line_msg: str) -> SingleInstructionInvalidArgumentException:
    return SingleInstructionInvalidArgumentException(single_line_msg)
