from shellcheck_lib.cli.cli_environment import exit_values
from shellcheck_lib.cli.cli_environment.command_line_options import OPTION_FOR_PREPROCESSOR
from shellcheck_lib.help.program_modes.test_case.contents.main.setup import Setup
from shellcheck_lib.help.utils.formatting import cli_option
from shellcheck_lib.util.textformat.parse import normalize_and_parse
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure.structures import *


def test_case_processing_documentation(setup: Setup) -> doc.SectionContents:
    preamble_paragraphs = normalize_and_parse(BEFORE_PHASE_LIST)
    paragraphs = (
        preamble_paragraphs +
        [processing_step_list(setup)]
    )
    return doc.SectionContents(
        paragraphs,
        []
    )


def processing_step_list(setup: Setup) -> ParagraphItem:
    return lists.HeaderContentList(
        [
            lists.HeaderContentListItem(
                text('preprocessing'),
                _step_description(normalize_and_parse(PURPOSE_OF_PREPROCESSING.format(
                    cli_option_for_preprocessor=cli_option(OPTION_FOR_PREPROCESSOR))),
                    FAILURE_CONDITION_OF_PREPROCESSING,
                    exit_values.NO_EXECUTION__PRE_PROCESS_ERROR)
            ),
            lists.HeaderContentListItem(
                text('syntax checking'),
                _step_description(normalize_and_parse(
                    PURPOSE_OF_SYNTAX_CHECKING),
                    FAILURE_CONDITION_OF_SYNTAX_CHECKING,
                    exit_values.NO_EXECUTION__PARSE_ERROR)
            ),
            lists.HeaderContentListItem(
                text('validation'),
                _step_description(
                    normalize_and_parse(PURPOSE_OF_VALIDATION.format(phase=setup.phase_names)),
                    FAILURE_CONDITION_OF_VALIDATION,
                    exit_values.EXECUTION__VALIDATE)
            ),
            lists.HeaderContentListItem(
                text('execution'),
                normalize_and_parse(EXECUTION_DESCRIPTION.format(phase=setup.phase_names)) +
                [execution_sub_steps_description(setup)] +
                normalize_and_parse(OUTCOME_OF_EXECUTION.format(phase=setup.phase_names))),
        ],
        lists.Format(lists.ListType.ORDERED_LIST,
                     custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS)
    )


def _step_description(purpose_paragraphs: list,
                      failure_condition: ParagraphItem,
                      exit_value_on_error: exit_values.ExitValue) -> list:
    outcome_on_error = first_column_is_header_table([
        [[para('Exit code')], [para(str(exit_value_on_error.exit_code))]],
        [[para('Stdout')], [para(exit_value_on_error.exit_identifier)]],
    ])
    return purpose_paragraphs + [failure_condition, outcome_on_error]


BEFORE_PHASE_LIST = """\
A test case file is processed in a number of steps,
where the actual execution of the test is the last step.


The outcome of the processing is reported by an exitcode and an identifier printed as a single line on stdout.


If a step before the execution fails, then the outcome is reported and the processing is halted.
"""

PURPOSE_OF_PREPROCESSING = """\
Transforms the test case file.


This step is applied only if a preprocessor has been given by {cli_option_for_preprocessor}.
"""

FAILURE_CONDITION_OF_PREPROCESSING = para(
    'Fails if the preprocessor program cannot be executed, '
    'or if it exits with a non-zero exit code.')

PURPOSE_OF_SYNTAX_CHECKING = 'Checks the syntax of all elements in the test case file.'

FAILURE_CONDITION_OF_SYNTAX_CHECKING = para('Fails if a syntax error is found.')

PURPOSE_OF_VALIDATION = """\
Checks references to external resources, files etc.


Validation is actually done in two steps.
Fist this step, and then one step directly after the {phase[setup]} phase has executed.

This second step validates the effect of the {phase[setup]} phase.


The reason for having this second step is to avoid errors caused by errors
in the setup, rather than errors in the tested program.
"""

FAILURE_CONDITION_OF_VALIDATION = para('Fails if an unresolved file reference is found, e.g.')

EXECUTION_DESCRIPTION = """\
Executes the actual test.


One validation step is embedded in the execution:"""


def execution_sub_steps_description(setup: Setup) -> ParagraphItem:
    return lists.HeaderContentList([
        lists.HeaderContentListItem(
            text('execution of {phase[setup]:syntax}'.format(phase=setup.phase_names)),
            []),
        lists.HeaderContentListItem(
            text('post {phase[setup]:syntax} validation'.format(phase=setup.phase_names)),
            []),
        lists.HeaderContentListItem(
            text('execution of remaining phases'),
            []),
    ],
        lists.Format(lists.ListType.ORDERED_LIST,
                     custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS)
    )


OUTCOME_OF_EXECUTION = """\
If the validation step fails, then the outcome of the test will be the same as a failure in
the validation step before execution (se above).

Otherwise, the outcome depends on the outcome of the {phase[assert]} phase.
"""
