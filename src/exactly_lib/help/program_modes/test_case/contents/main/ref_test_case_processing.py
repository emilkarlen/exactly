from exactly_lib.cli.cli_environment.program_modes.test_case import exit_values
from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import OPTION_FOR_PREPROCESSOR__LONG
from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup, post_setup_validation_step_name, \
    step_with_single_exit_value
from exactly_lib.help.utils.formatting import cli_option
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs


def test_case_processing_documentation(setup: Setup) -> docs.SectionContents:
    preamble_paragraphs = normalize_and_parse(BEFORE_STEP_LIST)
    paragraphs = (
        preamble_paragraphs +
        [processing_step_list(setup)]
    )
    return docs.SectionContents(
        paragraphs,
        []
    )


def processing_step_list(setup: Setup) -> docs.ParagraphItem:
    items = [
        docs.list_item('preprocessing',
                       step_with_single_exit_value(
                           normalize_and_parse(PURPOSE_OF_PREPROCESSING.format(
                               cli_option_for_preprocessor=cli_option(OPTION_FOR_PREPROCESSOR__LONG))),
                           FAILURE_CONDITION_OF_PREPROCESSING,
                           exit_values.NO_EXECUTION__PRE_PROCESS_ERROR)
                       ),
        docs.list_item('syntax checking',
                       step_with_single_exit_value(
                           normalize_and_parse(PURPOSE_OF_SYNTAX_CHECKING),
                           FAILURE_CONDITION_OF_SYNTAX_CHECKING,
                           exit_values.NO_EXECUTION__PARSE_ERROR)
                       ),
        docs.list_item('validation',
                       step_with_single_exit_value(
                           normalize_and_parse(PURPOSE_OF_VALIDATION.format(phase=setup.phase_names)),
                           FAILURE_CONDITION_OF_VALIDATION,
                           exit_values.EXECUTION__VALIDATE)
                       ),
        docs.list_item('execution',
                       normalize_and_parse(EXECUTION_DESCRIPTION.format(phase=setup.phase_names)) +
                       [execution_sub_steps_description(setup)] +
                       normalize_and_parse(OUTCOME_OF_EXECUTION.format(phase=setup.phase_names))),
    ]
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.ORDERED_LIST,
                                                custom_separations=docs.SEPARATION_OF_HEADER_AND_CONTENTS)
                                   )


BEFORE_STEP_LIST = """\
A test case file is processed in a number of steps,
where the actual execution of the test is the last step.


The outcome is reported by an exitcode and an identifier printed as a single line on stdout.


If a step before the execution fails, then the outcome is reported and the processing is halted.
"""

PURPOSE_OF_PREPROCESSING = """\
Transforms the test case file.


This step is applied only if a preprocessor has been given by {cli_option_for_preprocessor}.
"""

FAILURE_CONDITION_OF_PREPROCESSING = docs.para(
    'Fails if the preprocessor program cannot be executed, '
    'or if it exits with a non-zero exit code.')

PURPOSE_OF_SYNTAX_CHECKING = 'Checks the syntax of all elements in the test case file.'

FAILURE_CONDITION_OF_SYNTAX_CHECKING = docs.para('Fails if a syntax error is found.')

PURPOSE_OF_VALIDATION = """\
Checks references to external resources, files etc.


Validation is actually done in two steps.
Fist this step, and then one step directly after the {phase[setup]} phase has executed.

This second step validates the effect of the {phase[setup]} phase.


The reason for having this second step is to avoid errors caused by errors
in the setup, rather than errors in the tested program.
"""

FAILURE_CONDITION_OF_VALIDATION = docs.para('Fails if an unresolved file reference is found, e.g.')

EXECUTION_DESCRIPTION = """\
Executes the actual test.


One validation step is embedded in the execution:"""


def execution_sub_steps_description(setup: Setup) -> docs.ParagraphItem:
    return lists.HeaderContentList([
        lists.HeaderContentListItem(
            docs.text('execution of {phase[setup]:syntax}'.format(phase=setup.phase_names)),
            []),
        lists.HeaderContentListItem(
            docs.text(post_setup_validation_step_name(setup)),
            []),
        lists.HeaderContentListItem(
            docs.text('execution of remaining phases'),
            []),
    ],
        lists.Format(lists.ListType.ORDERED_LIST,
                     custom_separations=docs.SEPARATION_OF_HEADER_AND_CONTENTS)
    )


OUTCOME_OF_EXECUTION = """\
If the "post {phase[setup]:syntax} validation" fails,
then the outcome of the test will be the same as a failure in
the validation step before execution (se above).

Otherwise, the outcome depends on the outcome of the {phase[assert]} phase.
"""
