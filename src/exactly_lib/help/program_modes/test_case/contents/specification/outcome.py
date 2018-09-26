from exactly_lib import program_info
from exactly_lib.cli.definitions import exit_codes
from exactly_lib.common.exit_value import ExitValue
from exactly_lib.definitions import formatting
from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.doc_format import exit_value_text
from exactly_lib.definitions.entity import conf_params, directives
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.execution.full_execution.result import FullExeResultStatus
from exactly_lib.execution.partial_execution.result import PartialExeResultStatus
from exactly_lib.help.program_modes.test_case.contents.specification.processing import \
    FAILURE_CONDITION_OF_PREPROCESSING
from exactly_lib.help.program_modes.test_case.contents.specification.utils import Setup, \
    post_setup_validation_step_name, \
    step_with_single_exit_value, singe_exit_value_display, step_with_single_exit_value2
from exactly_lib.processing import exit_values
from exactly_lib.test_case import test_case_status
from exactly_lib.util.textformat.constructor import sections, paragraphs
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.section_target_hierarchy import hierarchies as h, generator
from exactly_lib.util.textformat.structure.structures import *
from exactly_lib.util.textformat.textformat_parser import TextParser


def root(header: str, setup: Setup) -> generator.SectionHierarchyGenerator:
    preamble_paragraphs = normalize_and_parse(PREAMBLE)

    def const_contents(header_: str, paragraphs: List[ParagraphItem]) -> generator.SectionHierarchyGenerator:
        return h.leaf(header_,
                      sections.constant_contents(section_contents(paragraphs)))

    return h.hierarchy(
        header,
        paragraphs.constant(preamble_paragraphs),
        [
            h.child('reporting',
                    const_contents('Reporting',
                                   TEXT_PARSER.fnap(REPORTING))

                    ),
            h.child('scenarios',
                    h.hierarchy(
                        'Scenarios',
                        children=[
                            h.child('complete-execution',
                                    const_contents('Complete execution',
                                                   _description_of_complete_execution(setup))

                                    ),
                            h.child('error-during-validation',
                                    const_contents('Error during validation',
                                                   _error_in_validation_before_execution())

                                    ),
                            h.child('error-during-execution',
                                    const_contents('Error during execution',
                                                   _interrupted_execution(setup))

                                    ),
                            h.child('other-errors',
                                    const_contents('Other errors',
                                                   _other_errors(setup))

                                    ),
                        ]
                    )),
            h.child('summary-of-exit-codes',
                    const_contents(ALL_EXIT_VALUES_SUMMARY_TABLE_HEADER,
                                   [all_exit_values_summary_table()]
                                   )

                    ),
        ]
    )


TEXT_PARSER = TextParser({
    'phase': phase_names.PHASE_NAME_DICTIONARY,
    'test_case_status': formatting.conf_param(conf_params.TEST_CASE_STATUS_CONF_PARAM_INFO.informative_name),
    'default_status': test_case_status.NAME_DEFAULT,
    'an_error_in_source': misc_texts.SYNTAX_ERROR_NAME.singular_determined,
    'an_exit_code': misc_texts.EXIT_CODE.singular_determined,
    'an_exit_identifier': misc_texts.EXIT_IDENTIFIER.singular_determined,
    'including': formatting.keyword(directives.INCLUDING_DIRECTIVE_INFO.singular_name),
})

PREAMBLE = ''

REPORTING = """\
Outcome is reported either as {an_exit_code}, or as an exit code together with {an_exit_identifier} printed as a single
line on stdout.
"""


def _description_of_complete_execution(setup: Setup) -> List[ParagraphItem]:
    ret_val = []
    ret_val.extend(TEXT_PARSER.fnap(COMPLETE_EXECUTION_OUTCOME_DEPENDS_ON_TWO_THINGS))
    ret_val.append(_what_outcome_depends_on(TEXT_PARSER))
    ret_val.extend(TEXT_PARSER.fnap(TABLE_INTRO))
    ret_val.append(_outcomes_per_status_and_assert(setup))
    ret_val.extend(TEXT_PARSER.fnap(OUTCOME_IS_EXIT_CODE_AND_IDENTIFIER))
    ret_val.append(_exit_value_table_for_full_execution())
    return ret_val


COMPLETE_EXECUTION_OUTCOME_DEPENDS_ON_TWO_THINGS = """\
The outcome of a completely executed test case depends on two things:
"""

TABLE_INTRO = """\
Together, these determine the outcome of the test case as a whole:
"""


def _what_outcome_depends_on(tp: TextParser) -> ParagraphItem:
    items = [
        list_item(tp.text(_OUTCOME_DEPENDENCE__STATUS),
                  tp.fnap(_OUTCOME_DEFAULT_STATUS)),
        list_item(tp.text(_OUTCOME_DEPENDENCE__ASSERT_PHASE)),
    ]
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.ORDERED_LIST,
                                                custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS))


_OUTCOME_DEPENDENCE__STATUS = """\
The {test_case_status} set by the {phase[conf]} phase.
"""

_OUTCOME_DEFAULT_STATUS = """\
The default is {default_status}.
"""

_OUTCOME_DEPENDENCE__ASSERT_PHASE = """\
The outcome of the {phase[assert]} phase.
"""


def _outcomes_per_status_and_assert(setup: Setup) -> ParagraphItem:
    def _row(tc_status: str, assert_outcome: PartialExeResultStatus, test_outcome: FullExeResultStatus) -> list:
        return [cell(paras(tc_status)),
                cell(paras(assert_outcome.name if assert_outcome is not None else '')),
                cell(paras(test_outcome.name)),
                ]

    return first_row_is_header_table([
        [
            cell(paras(conf_params.TEST_CASE_STATUS_CONF_PARAM_INFO.singular_name.capitalize())),
            cell(paras('{phase[assert]:syntax}'.format(phase=setup.phase_names))),
            cell(paras('Test Case')),
        ],
        _row(test_case_status.NAME_PASS, PartialExeResultStatus.PASS, FullExeResultStatus.PASS),
        _row(test_case_status.NAME_PASS, PartialExeResultStatus.FAIL, FullExeResultStatus.FAIL),

        _row(test_case_status.NAME_FAIL, PartialExeResultStatus.PASS, FullExeResultStatus.XPASS),
        _row(test_case_status.NAME_FAIL, PartialExeResultStatus.FAIL, FullExeResultStatus.XFAIL),

        _row(test_case_status.NAME_SKIP, None, FullExeResultStatus.SKIPPED),
    ],
        '  ')


def _interrupted_execution(setup: Setup) -> List[ParagraphItem]:
    ret_val = []
    ret_val += normalize_and_parse(_INTERRUPTED_EXECUTION_PREAMBLE.format(phase=setup.phase_names))
    ret_val += TEXT_PARSER.fnap(OUTCOME_IS_EXIT_CODE_AND_IDENTIFIER)
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
                      exit_values.EXECUTION__VALIDATION_ERROR)
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
                      _failure_condition_of_implementation_error(),
                      exit_values.EXECUTION__IMPLEMENTATION_ERROR)
                  ),
    ]
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.ITEMIZED_LIST,
                                                custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS)
                                   )


def _error_in_validation_before_execution() -> List[ParagraphItem]:
    ret_val = []
    ret_val += TEXT_PARSER.fnap(_ERROR_IN_VALIDATION_BEFORE_EXECUTION_PREAMBLE)
    ret_val += TEXT_PARSER.fnap(OUTCOME_IS_EXIT_CODE_AND_IDENTIFIER)
    ret_val.append(singe_exit_value_display(exit_values.EXECUTION__VALIDATION_ERROR))
    return ret_val


_ERROR_IN_VALIDATION_BEFORE_EXECUTION_PREAMBLE = """\
If validation fails, the test case is not executed.
"""


# def _exit_value_table_for_all_exit_values() -> ParagraphItem:
#     return _outcome_and_exit_value_table_for(exit_values.ALL_EXIT_VALUES)


def _exit_value_table_for(exit_value_list: List[ExitValue]) -> ParagraphItem:
    def _row(exit_value: ExitValue) -> List[TableCell]:
        return [
            cell(paras(exit_value_text(exit_value))),
            cell(paras(str(exit_value.exit_code))),
        ]

    return first_row_is_header_table(
        [
            [
                cell(paras(misc_texts.EXIT_IDENTIFIER_TITLE)),
                cell(paras(misc_texts.EXIT_CODE_TITLE))
            ]] +
        [_row(exit_value) for exit_value in exit_value_list],
        '  ')


def _outcome_and_exit_value_table_for(exit_value_list: List[ExitValue]) -> ParagraphItem:
    def _row(exit_value: ExitValue) -> List[TableCell]:
        return [
            cell(paras(exit_value.exit_identifier)),
            cell(paras(exit_value_text(exit_value))),
            cell(paras(str(exit_value.exit_code))),
        ]

    return first_row_is_header_table(
        [
            [
                cell(paras('Test Case')),
                cell(paras(misc_texts.EXIT_IDENTIFIER_TITLE)),
                cell(paras(misc_texts.EXIT_CODE_TITLE)),
            ]] +
        [_row(exit_value) for exit_value in exit_value_list],
        '  ')


def _exit_value_table_for_full_execution() -> ParagraphItem:
    return _outcome_and_exit_value_table_for([
        exit_values.EXECUTION__PASS,
        exit_values.EXECUTION__FAIL,
        exit_values.EXECUTION__XPASS,
        exit_values.EXECUTION__XFAIL,
        exit_values.EXECUTION__SKIPPED,

    ])


ALL_EXIT_VALUES_SUMMARY_TABLE_HEADER = 'Summary of exit codes and identifiers'


def all_exit_values_summary_table() -> ParagraphItem:
    return _exit_value_table_for(sorted(exit_values.ALL_EXIT_VALUES,
                                        key=ExitValue.exit_identifier.fget))


def _failure_condition_of_post_setup_validation(setup: Setup) -> ParagraphItem:
    return para("""An instruction's """ + post_setup_validation_step_name(setup) + ' fails.')


def _failure_condition_of_hard_error(setup: Setup) -> ParagraphItem:
    return para("""An instruction fails to do it's job. E.g. an instruction in the {phase[setup]} """
                """phase fails to create a file.""".format(phase=setup.phase_names))


def _failure_condition_of_implementation_error() -> ParagraphItem:
    return para("""An error in the implementation of %s is detected.""" % _program_name())


def _program_name() -> str:
    return formatting.program_name(program_info.PROGRAM_NAME)


OUTCOME_IS_EXIT_CODE_AND_IDENTIFIER = """\
The outcome is reported by {an_exit_code} and {an_exit_identifier} printed as a single
line on stdout.
"""


def _other_errors(setup: Setup) -> List[ParagraphItem]:
    ret_val = []
    ret_val.extend(normalize_and_parse(_CLI_PARSING_ERROR.format(program_name=_program_name(),
                                                                 EXIT_CODE=exit_codes.EXIT_INVALID_USAGE)))
    ret_val.extend(normalize_and_parse(_OTHER_NON_CLI_ERRORS))
    ret_val.append(_other_non_cli_errors())
    return ret_val


_CLI_PARSING_ERROR = """\
If parsing of command line arguments fails,
{program_name} halts with exit code {EXIT_CODE} (no exit identifier is printed).
"""

_OTHER_NON_CLI_ERRORS = """\
Otherwise an exit identifier is printed as a single line on stdout.


The following errors may occur:
"""


def _other_non_cli_errors() -> ParagraphItem:
    items = [
        list_item('File access',
                  step_with_single_exit_value(
                      [],
                      TEXT_PARSER.para(_FILE_ACCESS_ERROR),
                      exit_values.NO_EXECUTION__FILE_ACCESS_ERROR)
                  ),
        list_item('Preprocessing',
                  step_with_single_exit_value(
                      [],
                      TEXT_PARSER.para(FAILURE_CONDITION_OF_PREPROCESSING),
                      exit_values.NO_EXECUTION__PRE_PROCESS_ERROR)
                  ),
        list_item('Syntax checking',
                  step_with_single_exit_value2(
                      [],
                      TEXT_PARSER.fnap(_SYNTAX_ERROR),
                      exit_values.NO_EXECUTION__SYNTAX_ERROR)
                  ),
    ]
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.ITEMIZED_LIST,
                                                custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS)
                                   )


_FILE_ACCESS_ERROR = 'Failure of accessing a file on the command line or referenced via {including}.'

_SYNTAX_ERROR = """\
Fails if the test case contains {an_error_in_source}.


Also fails if the test case is run as part of a test suite,
and the test suite contains {an_error_in_source}.
"""
