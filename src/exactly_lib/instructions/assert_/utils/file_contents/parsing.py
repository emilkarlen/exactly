import re

from exactly_lib import program_info
from exactly_lib.cli.util.cli_argument_syntax import long_option_name
from exactly_lib.execution import environment_variables
from exactly_lib.help.utils import formatting
from exactly_lib.instructions.assert_.utils.file_contents import actual_file_transformers
from exactly_lib.instructions.assert_.utils.file_contents.actual_file_transformers import ActualFileTransformer
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.utils.arg_parse import parse_here_doc_or_file_ref
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_parsing import matches
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs

WITH_REPLACED_ENV_VARS_OPTION_NAME = a.OptionName(long_name='with-replaced-env-vars')
WITH_REPLACED_ENV_VARS_OPTION = long_option_name(WITH_REPLACED_ENV_VARS_OPTION_NAME.long)

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
                               arguments: list,
                               source: SingleInstructionParserSource) -> AssertPhaseInstruction:
    def _parse_empty(negated: bool,
                     actual: ComparisonActualFile,
                     extra_arguments: list) -> AssertPhaseInstruction:
        _ensure_no_more_arguments(extra_arguments)
        from exactly_lib.instructions.assert_.utils.file_contents.instruction_for_emptieness import \
            EmptinessAssertionInstruction
        return EmptinessAssertionInstruction(not negated, actual)

    def _parse_equals(negated: bool,
                      actual_file_transformer: ActualFileTransformer,
                      actual: ComparisonActualFile,
                      extra_arguments: list) -> AssertPhaseInstruction:
        (here_doc_or_file_ref_for_expected, remaining_arguments) = parse_here_doc_or_file_ref.parse(extra_arguments,
                                                                                                    source)
        _ensure_no_more_arguments(remaining_arguments)

        from exactly_lib.instructions.assert_.utils.file_contents.instruction_for_equality import \
            EqualsAssertionInstruction
        return EqualsAssertionInstruction(here_doc_or_file_ref_for_expected, actual, actual_file_transformer)

    def _parse_contains(negated: bool,
                        actual_file_transformer: ActualFileTransformer,
                        actual: ComparisonActualFile,
                        extra_arguments: list) -> AssertPhaseInstruction:
        if not extra_arguments:
            raise _parse_exception('Missing reg ex argument')
        reg_ex_argument = extra_arguments[0]
        del extra_arguments[0]
        _ensure_no_more_arguments(extra_arguments)
        try:
            reg_ex = re.compile(reg_ex_argument)
        except Exception as ex:
            raise _parse_exception("Invalid reg ex: '{}'".format(str(ex)))
        from exactly_lib.instructions.assert_.utils.file_contents import instruction_for_contains
        if negated:
            file_checker = instruction_for_contains.FileCheckerForNegativeMatch(reg_ex)
        else:
            file_checker = instruction_for_contains.FileCheckerForPositiveMatch(reg_ex)
        return instruction_for_contains.ContainsAssertionInstruction(file_checker, actual, actual_file_transformer)

    def _parse_contents(actual: ComparisonActualFile,
                        extra_arguments: list) -> AssertPhaseInstruction:
        with_replaced_env_vars = False
        if extra_arguments and matches(WITH_REPLACED_ENV_VARS_OPTION_NAME, extra_arguments[0]):
            with_replaced_env_vars = True
            del extra_arguments[0]
        actual_file_transformer = actual_file_transformers.IdentityFileTransformer()
        if with_replaced_env_vars:
            actual_file_transformer = actual_file_transformer_for_replace_env_vars
        if not extra_arguments:
            return _missing_operator([NOT_ARGUMENT, EQUALS_ARGUMENT, CONTAINS_ARGUMENT])
        negated = False
        if extra_arguments[0] == NOT_ARGUMENT:
            negated = True
            del extra_arguments[0]
        if not extra_arguments:
            return _missing_operator([EQUALS_ARGUMENT, CONTAINS_ARGUMENT])
        if extra_arguments[0] == CONTAINS_ARGUMENT:
            return _parse_contains(negated, actual_file_transformer, actual, extra_arguments[1:])
        if extra_arguments[0] == EQUALS_ARGUMENT:
            return _parse_equals(negated, actual_file_transformer, actual, extra_arguments[1:])
        raise _parse_exception('Unknown operator: {}'.format(extra_arguments[0]))

    if arguments[0] == EMPTY_ARGUMENT:
        return _parse_empty(False, actual_file, arguments[1:])
    elif arguments[:2] == [NOT_ARGUMENT, EMPTY_ARGUMENT]:
        return _parse_empty(True, actual_file, arguments[2:])
    else:
        return _parse_contents(actual_file, arguments)


def _missing_operator(operators: list) -> AssertPhaseInstruction:
    msg = 'Missing operator: {}'.format('|'.join(operators))
    raise SingleInstructionInvalidArgumentException(msg)


def _ensure_no_more_arguments(remaining_arguments: list):
    if remaining_arguments:
        raise _parse_exception('Superfluous arguments: {}'.format(remaining_arguments))


def _parse_exception(single_line_msg: str) -> SingleInstructionInvalidArgumentException:
    return SingleInstructionInvalidArgumentException(single_line_msg)
