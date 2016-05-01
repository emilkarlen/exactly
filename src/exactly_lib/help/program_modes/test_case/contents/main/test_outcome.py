import exactly_lib.execution.execution_mode
from exactly_lib import program_info
from exactly_lib.cli.cli_environment.exit_value import ExitValue
from exactly_lib.cli.cli_environment.program_modes.test_case import exit_values
from exactly_lib.execution.result import PartialResultStatus, FullResultStatus
from exactly_lib.help.program_modes.test_case.contents.main.ref_test_case_processing import \
    FAILURE_CONDITION_OF_PREPROCESSING
from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup, post_setup_validation_step_name, \
    step_with_single_exit_value, singe_exit_value_display
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure.structures import *

EXIT_CODE_FROM_ARGUMENT_PARSER = 2


def test_outcome_documentation(setup: Setup) -> SectionContents:
    preamble_paragraphs = normalize_and_parse(PREAMBLE)
    return SectionContents(
        preamble_paragraphs,
        [
            section('Reporting',
                    normalize_and_parse(REPORTING)),
            section('Successful execution of test case',
                    _description_of_full_execution(setup)),
            section('Error during execution',
                    _interrupted_execution(setup)),
            section('Error during validation (before execution)',
                    _error_in_validation_before_execution(setup)),
            section('Other errors',
                    _other_errors(setup)),
            section('Summary of exit codes and identifiers',
                    [_exit_value_table_for(setup,
                                           sorted(exit_values.ALL_EXIT_VALUES,
                                                  key=ExitValue.exit_identifier.fget))]),
        ]
    )


PREAMBLE = ''

REPORTING = """\
Outcome is reported either as an exit code, or as an exit code together with an identifier printed as a single
line on stdout.
"""


def _description_of_full_execution(setup: Setup) -> list:
    ret_val = []
    ret_val.extend(normalize_and_parse(FULL_EXECUTION_OUTCOME_DEPENDS_ON_TWO_THINGS))
    ret_val.append(_what_outcome_depends_on(setup))
    ret_val.append(_outcomes_per_mode_and_assert(setup))
    ret_val.append(para(OUTCOME_IS_EXIT_CODE_AND_IDENTIFIER))
    ret_val.append(_exit_value_table_for_full_execution(setup))
    return ret_val


FULL_EXECUTION_OUTCOME_DEPENDS_ON_TWO_THINGS = """The outcome of a fully executed test case depends on two things:"""


def _what_outcome_depends_on(setup: Setup) -> ParagraphItem:
    items = [
        list_item("""The "execution mode" set by the {phase[conf]} phase""".format(phase=setup.phase_names),
                  [para('The default mode is {default_mode}.'.format(
                      default_mode=exactly_lib.execution.execution_mode.NAME_NORMAL))]),
        list_item("""The outcome of the {phase[assert]} phase""".format(phase=setup.phase_names),
                  []),
    ]
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.ORDERED_LIST,
                                                custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS))


def _outcomes_per_mode_and_assert(setup: Setup) -> ParagraphItem:
    def _row(mode: str, assert_outcome: PartialResultStatus, test_outcome: FullResultStatus) -> list:
        return [paras(mode),
                paras(assert_outcome.name if assert_outcome is not None else ''),
                paras(test_outcome.name)
                ]

    return first_row_is_header_table([
        [
            paras('Mode'),
            paras('{phase[assert]:syntax}'.format(phase=setup.phase_names)),
            paras('Test Case')],
        _row(exactly_lib.execution.execution_mode.NAME_NORMAL, PartialResultStatus.PASS, FullResultStatus.PASS),
        _row(exactly_lib.execution.execution_mode.NAME_NORMAL, PartialResultStatus.FAIL, FullResultStatus.FAIL),

        _row(exactly_lib.execution.execution_mode.NAME_XFAIL, PartialResultStatus.PASS, FullResultStatus.XPASS),
        _row(exactly_lib.execution.execution_mode.NAME_XFAIL, PartialResultStatus.FAIL, FullResultStatus.XFAIL),

        _row(exactly_lib.execution.execution_mode.NAME_SKIP, None, FullResultStatus.SKIPPED),
    ],
        '  ')


def _interrupted_execution(setup: Setup) -> list:
    ret_val = []
    ret_val.extend(normalize_and_parse(_INTERRUPTED_EXECUTION_PREAMBLE.format(phase=setup.phase_names)))
    ret_val.append(para(OUTCOME_IS_EXIT_CODE_AND_IDENTIFIER))
    ret_val.append(para(_INTERRUPTED_EXECUTION_CAUSES))
    ret_val.append(interrupted_execution_list(setup))
    return ret_val


_INTERRUPTED_EXECUTION_PREAMBLE = """\
If an error occur during the execution of a test, then this will halt the test and
be reported as an error, and not as a failed test.


Note that an error will be reported even if
both the {phase[act]} and {phase[assert]} phases have been executed successfully.
"""

_INTERRUPTED_EXECUTION_CAUSES = """The execution may be interrupted by the following causes:"""


def interrupted_execution_list(setup: Setup) -> ParagraphItem:
    items = [
        list_item('Failure of ' + post_setup_validation_step_name(setup),
                  step_with_single_exit_value(
                      [],
                      _failure_condition_of_post_setup_validation(setup),
                      exit_values.EXECUTION__VALIDATE)
                  ),
        list_item('Hard error',
                  step_with_single_exit_value(
                      [],
                      _failure_condition_of_hard_error(setup),
                      exit_values.EXECUTION__HARD_ERROR)
                  ),
        list_item('Implementation error',
                  step_with_single_exit_value(
                      [],
                      _failure_condition_of_implementation_error(setup),
                      exit_values.EXECUTION__IMPLEMENTATION_ERROR)
                  ),
    ]
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.ITEMIZED_LIST,
                                                custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS)
                                   )


def _error_in_validation_before_execution(setup: Setup) -> list:
    ret_val = []
    ret_val.extend(normalize_and_parse(_ERROR_IN_VALIDATION_BEFORE_EXECUTION_PREAMBLE))
    ret_val.append(para(OUTCOME_IS_EXIT_CODE_AND_IDENTIFIER))
    ret_val.append(singe_exit_value_display(exit_values.EXECUTION__VALIDATE))
    return ret_val


_ERROR_IN_VALIDATION_BEFORE_EXECUTION_PREAMBLE = """\
If validation fails, the test case is not executed.
"""


def _exit_value_table_for_all_exit_values(setup: Setup) -> ParagraphItem:
    return _outcome_and_exit_value_table_for(setup, exit_values.ALL_EXIT_VALUES)


def _exit_value_table_for(setup: Setup,
                          exit_value_list: list) -> ParagraphItem:
    def _row(exit_value: ExitValue) -> list:
        return [paras(exit_value.exit_identifier),
                paras(str(exit_value.exit_code)),
                ]

    return first_row_is_header_table(
        [
            [
                paras('Exit identifier'),
                paras('Exit code')
            ]] +
        [_row(exit_value) for exit_value in exit_value_list],
        '  ')


def _outcome_and_exit_value_table_for(setup: Setup,
                                      exit_value_list: list) -> ParagraphItem:
    def _row(exit_value: ExitValue) -> list:
        return [paras(exit_value.exit_identifier),
                paras(exit_value.exit_identifier),
                paras(str(exit_value.exit_code)),
                ]

    return first_row_is_header_table(
        [
            [
                paras('Test Case'),
                paras('Exit identifier'),
                paras('Exit code')
            ]] +
        [_row(exit_value) for exit_value in exit_value_list],
        '  ')


def _exit_value_table_for_full_execution(setup: Setup) -> ParagraphItem:
    return _outcome_and_exit_value_table_for(setup,
                                             [
                                                 exit_values.EXECUTION__PASS,
                                                 exit_values.EXECUTION__FAIL,
                                                 exit_values.EXECUTION__XPASS,
                                                 exit_values.EXECUTION__XFAIL,
                                                 exit_values.EXECUTION__SKIPPED,

                                             ])


def _failure_condition_of_post_setup_validation(setup: Setup) -> ParagraphItem:
    return para("""An instruction's """ + post_setup_validation_step_name(setup) + ' fails.')


def _failure_condition_of_hard_error(setup: Setup) -> ParagraphItem:
    return para("""An instruction fails to do it's job. E.g. an instruction in the {phase[setup]} """
                """phase fails to create a file.""".format(phase=setup.phase_names))


def _failure_condition_of_implementation_error(setup: Setup) -> ParagraphItem:
    return para("""An error in the implementation of %s is detected.""" % program_info.PROGRAM_NAME)


OUTCOME_IS_EXIT_CODE_AND_IDENTIFIER = (
    'The outcome is reported by an exitcode and an identifier printed as a single '
    'line on stdout.')


def _other_errors(setup: Setup) -> list:
    ret_val = []
    ret_val.extend(normalize_and_parse(_CLI_PARSING_ERROR.format(program_name=program_info.PROGRAM_NAME,
                                                                 EXIT_CODE=EXIT_CODE_FROM_ARGUMENT_PARSER)))
    ret_val.extend(normalize_and_parse(_OTHER_NON_CLI_ERRORS))
    ret_val.append(_other_non_cli_errors(setup))
    return ret_val


_CLI_PARSING_ERROR = """\
If parsing of command line arguments fails,
{program_name} halts with exit code {EXIT_CODE} (no exit identifier is printed).
"""

_OTHER_NON_CLI_ERRORS = """\
Otherwise an exit identifier is printed as a single line on stdout.


The following errors may occur:
"""


def _other_non_cli_errors(setup: Setup) -> ParagraphItem:
    items = [
        list_item('File access',
                  step_with_single_exit_value(
                      [],
                      para('Failure of accessing a file on the command line.'),
                      exit_values.NO_EXECUTION__FILE_ACCESS_ERROR)
                  ),
        list_item('Preprocessing',
                  step_with_single_exit_value(
                      [],
                      FAILURE_CONDITION_OF_PREPROCESSING,
                      exit_values.NO_EXECUTION__PRE_PROCESS_ERROR)
                  ),
        list_item('Syntax checking',
                  step_with_single_exit_value(
                      [],
                      para('Fails if the test case contains a syntax error.'),
                      exit_values.NO_EXECUTION__PARSE_ERROR)
                  ),
    ]
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.ITEMIZED_LIST,
                                                custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS)
                                   )
