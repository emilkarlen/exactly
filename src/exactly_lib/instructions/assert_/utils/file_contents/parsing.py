import re

from exactly_lib import program_info
from exactly_lib.execution import environment_variables
from exactly_lib.help.utils import formatting
from exactly_lib.instructions.assert_.utils.file_contents import actual_file_transformers
from exactly_lib.instructions.assert_.utils.file_contents.actual_file_transformers import ActualFileTransformer
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.utils.arg_parse import parse_here_doc_or_file_ref
from exactly_lib.section_document.new_parse_source import ParseSource
from exactly_lib.section_document.parser_implementations import token_parse
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_parse import TokenType
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_parsing import matches
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs

WITH_REPLACED_ENV_VARS_OPTION_NAME = a.OptionName(long_name='with-replaced-env-vars')
WITH_REPLACED_ENV_VARS_OPTION = long_option_syntax(WITH_REPLACED_ENV_VARS_OPTION_NAME.long)

NOT_ARGUMENT = '!'
EMPTY_ARGUMENT = 'empty'
EQUALS_ARGUMENT = 'equals'
CONTAINS_ARGUMENT = 'contains'


def with_replaced_env_vars_help(checked_file: str) -> list:
    header_text = """\
    Every occurrence of a path that matches any of the {program_name} environment variables
    in {checked_file} is replaced with the name of the matching variable.
    (Variable values are replaced with variable names.)


    These environment variables are:
    """.format(program_name=formatting.program_name(program_info.PROGRAM_NAME),
               option=WITH_REPLACED_ENV_VARS_OPTION,
               checked_file=checked_file)
    variables_list = [docs.simple_header_only_list(sorted(environment_variables.ALL_REPLACED_ENV_VARS),
                                                   docs.lists.ListType.VARIABLE_LIST)]
    return normalize_and_parse(header_text) + variables_list


def parse_comparison_operation(actual_file: ComparisonActualFile,
                               actual_file_transformer_for_replace_env_vars: ActualFileTransformer,
                               source: ParseSource) -> AssertPhaseInstruction:
    def _parse_empty(negated: bool,
                     actual: ComparisonActualFile,
                     source: ParseSource) -> AssertPhaseInstruction:
        _ensure_no_more_arguments(source)
        from exactly_lib.instructions.assert_.utils.file_contents.instruction_for_emptieness import \
            EmptinessAssertionInstruction
        return EmptinessAssertionInstruction(not negated, actual)

    def _parse_equals(negated: bool,
                      actual_file_transformer: ActualFileTransformer,
                      actual: ComparisonActualFile,
                      source: ParseSource) -> AssertPhaseInstruction:
        here_doc_or_file_ref_for_expected = parse_here_doc_or_file_ref.parse_from_parse_source(source)
        _ensure_no_more_arguments(source)

        from exactly_lib.instructions.assert_.utils.file_contents.instruction_for_equality import \
            EqualsAssertionInstruction
        return EqualsAssertionInstruction(negated,
                                          here_doc_or_file_ref_for_expected,
                                          actual,
                                          actual_file_transformer)

    def _parse_contains(negated: bool,
                        actual_file_transformer: ActualFileTransformer,
                        actual: ComparisonActualFile,
                        source: ParseSource) -> AssertPhaseInstruction:
        reg_ex_arg = token_parse.parse_token_on_current_line(source, 'REG EX')
        _ensure_no_more_arguments(source)
        try:
            reg_ex = re.compile(reg_ex_arg.string)
        except Exception as ex:
            raise _parse_exception("Invalid reg ex: '{}'".format(str(ex)))
        from exactly_lib.instructions.assert_.utils.file_contents import instruction_for_contains
        if negated:
            file_checker = instruction_for_contains.FileCheckerForNegativeMatch(reg_ex)
        else:
            file_checker = instruction_for_contains.FileCheckerForPositiveMatch(reg_ex)
        return instruction_for_contains.ContainsAssertionInstruction(file_checker, actual, actual_file_transformer)

    def _parse_contents(actual: ComparisonActualFile,
                        source: ParseSource) -> AssertPhaseInstruction:
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
            next_arg_str = token_parse.parse_plain_token_on_current_line(source, 'OPERATION').string
        if next_arg_str == CONTAINS_ARGUMENT:
            return _parse_contains(negated, actual_file_transformer, actual, source)
        if next_arg_str == EQUALS_ARGUMENT:
            return _parse_equals(negated, actual_file_transformer, actual, source)
        raise _parse_exception('Unknown operator: {}'.format(next_arg_str))

    peek_source = source.copy
    first_argument = token_parse.parse_plain_token_on_current_line(peek_source).string
    if first_argument == EMPTY_ARGUMENT:
        source.catch_up_with(peek_source)
        return _parse_empty(False, actual_file, source)
    second_argument = token_parse.parse_token_on_current_line(peek_source)
    if second_argument.is_plain and [first_argument, second_argument.string] == [NOT_ARGUMENT, EMPTY_ARGUMENT]:
        source.catch_up_with(peek_source)
        return _parse_empty(True, actual_file, source)
    else:
        return _parse_contents(actual_file, source)


def _missing_operator(operators: list) -> AssertPhaseInstruction:
    msg = 'Missing operator: {}'.format('|'.join(operators))
    raise SingleInstructionInvalidArgumentException(msg)


def _ensure_no_more_arguments(source: ParseSource):
    if not source.is_at_eol__except_for_space:
        raise _parse_exception('Superfluous arguments: {}'.format(source.remaining_part_of_current_line))


def _parse_exception(single_line_msg: str) -> SingleInstructionInvalidArgumentException:
    return SingleInstructionInvalidArgumentException(single_line_msg)
