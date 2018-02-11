from exactly_lib import program_info
from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import OPTION_FOR_PREPROCESSOR
from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup, post_setup_validation_step_name, \
    step_with_single_exit_value
from exactly_lib.help.program_modes.test_case.contents.util import SectionContentsConstructorWithSetup
from exactly_lib.help_texts.entity.concepts import SYMBOL_CONCEPT_INFO
from exactly_lib.help_texts.formatting import cli_option, program_name
from exactly_lib.help_texts.misc_texts import SYNTAX_ERROR_NAME
from exactly_lib.processing import exit_values
from exactly_lib.util.textformat.construction.section_contents_constructor import ConstructionEnvironment
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.document import SectionContents


class ContentsConstructor(SectionContentsConstructorWithSetup):
    def __init__(self, setup: Setup):
        super().__init__(setup, {
            'phase': setup.phase_names,
            'program_name': program_name(program_info.PROGRAM_NAME),
            'symbol': SYMBOL_CONCEPT_INFO.name.singular,
            'symbols': SYMBOL_CONCEPT_INFO.name.plural,
            'cli_option_for_preprocessor': cli_option(OPTION_FOR_PREPROCESSOR),
            'an_error_in_source': SYNTAX_ERROR_NAME.singular_determined,
        })

    def apply(self, environment: ConstructionEnvironment) -> SectionContents:
        preamble_paragraphs = self.fnap(BEFORE_STEP_LIST)
        paragraphs = (
                preamble_paragraphs +
                [self.processing_step_list()]
        )
        return docs.SectionContents(
            paragraphs,
            []
        )

    def processing_step_list(self) -> docs.ParagraphItem:
        items = [
            docs.list_item('preprocessing',
                           step_with_single_exit_value(
                               self.fnap(PURPOSE_OF_PREPROCESSING),
                               self.text_parser.para(FAILURE_CONDITION_OF_PREPROCESSING),
                               exit_values.NO_EXECUTION__PRE_PROCESS_ERROR)
                           ),
            docs.list_item('syntax checking',
                           step_with_single_exit_value(
                               self.fnap(PURPOSE_OF_SYNTAX_CHECKING),
                               self.text_parser.para(FAILURE_CONDITION_OF_SYNTAX_CHECKING),
                               exit_values.NO_EXECUTION__SYNTAX_ERROR)
                           ),
            docs.list_item('validation',
                           step_with_single_exit_value(
                               self.fnap(PURPOSE_OF_VALIDATION),
                               self.text_parser.para(FAILURE_CONDITION_OF_VALIDATION),
                               exit_values.EXECUTION__VALIDATE)
                           ),
            docs.list_item('execution',
                           self.fnap(EXECUTION_DESCRIPTION) +
                           [self.execution_sub_steps_description()] +
                           self.fnap(OUTCOME_OF_EXECUTION)),
        ]
        return lists.HeaderContentList(items,
                                       lists.Format(lists.ListType.ORDERED_LIST,
                                                    custom_separations=docs.SEPARATION_OF_HEADER_AND_CONTENTS)
                                       )

    def execution_sub_steps_description(self) -> docs.ParagraphItem:
        return lists.HeaderContentList([
            docs.list_item(self.text_parser.text('execution of {phase[setup]:syntax}')),
            docs.list_item(docs.text(post_setup_validation_step_name(self.setup))),
            docs.list_item(docs.text('execution of remaining phases')),
        ],
            lists.Format(lists.ListType.ORDERED_LIST,
                         custom_separations=docs.SEPARATION_OF_HEADER_AND_CONTENTS)
        )


BEFORE_STEP_LIST = """\
Test case file "processing" starts after the command line arguments have been parsed,
and {program_name} has been told to run a test case.


A test case file is processed in a number of steps,
where the actual execution of the test is the last step.


The outcome is reported by an exitcode and an identifier printed as a single line on stdout.


If a step before the execution fails, then the outcome is reported and the processing is halted.
"""

PURPOSE_OF_PREPROCESSING = """\
Transforms the test case file.


This step is applied only if a preprocessor has been given by {cli_option_for_preprocessor},
or set in a test suite.
"""

FAILURE_CONDITION_OF_PREPROCESSING = """\
Fails if the preprocessor program cannot be executed, 
or if it exits with a non-zero exit code.
"""

PURPOSE_OF_SYNTAX_CHECKING = 'Checks the syntax of all elements in the test case file.'

FAILURE_CONDITION_OF_SYNTAX_CHECKING = 'Fails if {an_error_in_source} is found.'

PURPOSE_OF_VALIDATION = """\
Checks references to {symbols} and external resources (files etc).


Validation is actually done in two steps.
Fist this step, and then one step directly after the {phase[setup]} phase has executed.

This second step validates the effect of the {phase[setup]} phase.


The reason for having this second step is to make it easier to find errors caused by errors
in the setup, rather than errors in the tested program.
"""

FAILURE_CONDITION_OF_VALIDATION = """\
Fails if a reference to a {symbol}
that has not been defined or has invalid type,
is found,
or if a reference to a non-existing file is found, e.g.
"""

EXECUTION_DESCRIPTION = """\
Executes the actual test.


One validation step is embedded in the execution:"""

OUTCOME_OF_EXECUTION = """\
If the "post {phase[setup]:syntax} validation" fails,
then the outcome of the test will be the same as a failure in
the validation step before execution (see above).

Otherwise, the outcome depends on the outcome of the {phase[assert]} phase.
"""
