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
                _step_description([
                    para('Transforms the test case file.'),
                    para('This step is applied only if a preprocessor has been given by %s.' %
                         cli_option(OPTION_FOR_PREPROCESSOR))],
                    para('Fails if the preprocessor program cannot be executed, ' +
                         'or if it exits with a non-zero exit code.'),
                    exit_values.NO_EXECUTION__PRE_PROCESS_ERROR)
            ),
            lists.HeaderContentListItem(
                text('syntax checking'),
                _step_description([
                    para('Checks the syntax of all elements in the test case file.')],
                    para('Fails if a syntax error is found.'),
                    exit_values.NO_EXECUTION__PARSE_ERROR)
            ),
            lists.HeaderContentListItem(
                text('validation'),
                _step_description(
                    normalize_and_parse(VALIDATION_PURPOSE.format(phase=setup.phase_names)),
                    para('Fails if an unresolved file reference is found, e.g.'),
                    exit_values.EXECUTION__VALIDATE)
            ),
            lists.HeaderContentListItem(
                text('execution'),
                normalize_and_parse(EXECUTION_DESCRIPTION.format(phase=setup.phase_names))),
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

VALIDATION_PURPOSE = """\
Checks references to external resources, files etc.


Validation is done in two steps. One before the {phase[setup]} phase and one after.

The reason for this is to avoid errors in the {phase[act]} phase that results from invalid
setup, rather than errors in the tested program.
"""

EXECUTION_DESCRIPTION = """\
Executes the actual test.


Outcome depends on the outcome of the {phase[assert]} phase.
"""

"""
A test case file is processed by a sequence of steps:
preprocessing (if a preprocessor has been given)
syntax checking (aborting the test case if a syntax error is found)
validation (aborting the test case if an unresolved file reference is found, e.g.)
execution
"""
