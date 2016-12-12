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
from exactly_lib.util.string import lines_content
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs

WITH_REPLACED_ENV_VARS_OPTION_NAME = a.OptionName(long_name='with-replaced-env-vars')
WITH_REPLACED_ENV_VARS_OPTION = long_option_name(WITH_REPLACED_ENV_VARS_OPTION_NAME.long)

EMPTY_ARGUMENT = 'empty'
NOT_ARGUMENT = '!'
EQUALS_ARGUMENT = 'equals'
CONTAINS_ARGUMENT = 'matches'


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


def try_parse_content(actual_file: ComparisonActualFile,
                      actual_file_transformer_for_replace_env_vars: ActualFileTransformer,
                      arguments: list,
                      source: SingleInstructionParserSource) -> AssertPhaseInstruction:
    def _parse_empty(actual: ComparisonActualFile,
                     extra_arguments: list) -> AssertPhaseInstruction:
        if extra_arguments:
            raise SingleInstructionInvalidArgumentException(
                'file/{}: Extra arguments: {}'.format(EMPTY_ARGUMENT,
                                                      str(extra_arguments)))
        from exactly_lib.instructions.assert_.utils.file_contents.instruction_for_emptieness import \
            EmptinessAssertionInstruction
        return EmptinessAssertionInstruction(True, actual)

    def _parse_non_empty(actual: ComparisonActualFile,
                         extra_arguments: list) -> AssertPhaseInstruction:
        if extra_arguments:
            raise SingleInstructionInvalidArgumentException(
                'file/!{}: Extra arguments: {}'.format(EMPTY_ARGUMENT,
                                                       str(extra_arguments)))
        from exactly_lib.instructions.assert_.utils.file_contents.instruction_for_emptieness import \
            EmptinessAssertionInstruction
        return EmptinessAssertionInstruction(False, actual)

    def _parse_matches(actual_file_transformer: ActualFileTransformer,
                       actual: ComparisonActualFile,
                       extra_arguments: list) -> AssertPhaseInstruction:
        if not extra_arguments:
            raise SingleInstructionInvalidArgumentException(
                lines_content(['Missing regular expression argument']))
        if len(extra_arguments) > 1:
            raise SingleInstructionInvalidArgumentException(
                lines_content(['Superfluous arguments: {}'.format(extra_arguments[1:])]))
        reg_ex_argument = extra_arguments[0]
        try:
            reg_ex = re.compile(reg_ex_argument)
        except Exception as ex:
            raise SingleInstructionInvalidArgumentException(
                lines_content(['Invalid regular expression: {}',
                               str(ex)]))
        from exactly_lib.instructions.assert_.utils.file_contents.instruction_for_contains import \
            ContainsAssertionInstruction
        return ContainsAssertionInstruction(reg_ex, actual, actual_file_transformer)

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
            raise SingleInstructionInvalidArgumentException(
                lines_content(['Missing operator: {}'.format('|'.join([EQUALS_ARGUMENT, CONTAINS_ARGUMENT]))]))
        if extra_arguments[0] == CONTAINS_ARGUMENT:
            return _parse_matches(actual_file_transformer, actual, extra_arguments[1:])
        if extra_arguments[0] != EQUALS_ARGUMENT:
            raise SingleInstructionInvalidArgumentException(
                lines_content(['Unknown operator: {}'.format(extra_arguments[0])]))
        del extra_arguments[0]
        (here_doc_or_file_ref_for_expected, remaining_arguments) = parse_here_doc_or_file_ref.parse(extra_arguments,
                                                                                                    source)
        if remaining_arguments:
            raise SingleInstructionInvalidArgumentException(
                lines_content(['Superfluous arguments: {}'.format(remaining_arguments)]))

        from exactly_lib.instructions.assert_.utils.file_contents.instruction_for_equality import \
            EqualsAssertionInstruction
        return EqualsAssertionInstruction(here_doc_or_file_ref_for_expected, actual, actual_file_transformer)

    if arguments[0] == EMPTY_ARGUMENT:
        return _parse_empty(actual_file, arguments[1:])
    elif arguments[:2] == [NOT_ARGUMENT, EMPTY_ARGUMENT]:
        return _parse_non_empty(actual_file, arguments[2:])
    else:
        return _parse_contents(actual_file, arguments)
