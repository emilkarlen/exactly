from typing import List

from exactly_lib import program_info
from exactly_lib.cli.definitions.program_modes.test_case.command_line_options import OPTION_FOR_PREPROCESSOR
from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.definitions.entity import concepts, directives
from exactly_lib.definitions.test_case import phase_infos
from exactly_lib.help.program_modes.test_case.contents.specification.utils import Setup, \
    step_with_single_exit_value, step_with_multiple_exit_values
from exactly_lib.help.render import see_also
from exactly_lib.processing import exit_values
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import \
    SectionContentsConstructor
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.textformat_parser import TextParser


class ContentsConstructor(SectionContentsConstructor):
    def __init__(self, setup: Setup):
        self._setup = setup
        self._tp = TextParser({
            'phase': setup.phase_names,
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'instruction': concepts.INSTRUCTION_CONCEPT_INFO.name.singular,
            'instructions': concepts.INSTRUCTION_CONCEPT_INFO.name.plural,
            'ATC': concepts.ACTION_TO_CHECK_CONCEPT_INFO.singular_name,
            'act_phase': phase_infos.ACT.name,
            'symbol': concepts.SYMBOL_CONCEPT_INFO.name,
            'cli_option_for_preprocessor': formatting.cli_option(OPTION_FOR_PREPROCESSOR),
            'an_error_in_source': misc_texts.SYNTAX_ERROR_NAME.singular_determined,
            'directive': concepts.DIRECTIVE_CONCEPT_INFO.name,
            'including': formatting.keyword(directives.INCLUDING_DIRECTIVE_INFO.singular_name),
        })

    def apply(self, environment: ConstructionEnvironment) -> SectionContents:
        preamble_paragraphs = self._tp.fnap(BEFORE_STEP_LIST)
        paragraphs = (
                preamble_paragraphs +
                [self.processing_step_list()]
        )
        return docs.SectionContents(
            paragraphs,
            [
                see_also.SeeAlsoSectionConstructor(
                    see_also.items_of_targets(_see_also_targets())
                ).apply(environment)
            ]
        )

    def processing_step_list(self) -> docs.ParagraphItem:
        items = [
            docs.list_item('Preprocessing',
                           step_with_single_exit_value(
                               self._tp.fnap(PURPOSE_OF_PREPROCESSING),
                               self._tp.para(FAILURE_CONDITION_OF_PREPROCESSING),
                               exit_values.NO_EXECUTION__PRE_PROCESS_ERROR)
                           ),
            docs.list_item(self._tp.text('Syntax checking and {directive:s} processing'),
                           step_with_multiple_exit_values(
                               self._tp.fnap(PURPOSE_OF_SYNTAX_CHECKING),
                               self._tp.fnap(FAILURE_CONDITION_OF_SYNTAX_CHECKING),
                               [
                                   ('Syntax error', exit_values.NO_EXECUTION__SYNTAX_ERROR),
                                   ('File inclusion error', exit_values.NO_EXECUTION__FILE_ACCESS_ERROR),
                               ])
                           ),
            docs.list_item('Validation',
                           step_with_single_exit_value(
                               self._tp.fnap(PURPOSE_OF_VALIDATION),
                               self._tp.para(FAILURE_CONDITION_OF_VALIDATION),
                               exit_values.EXECUTION__VALIDATION_ERROR)
                           ),
            docs.list_item('Execution',
                           self._tp.fnap(EXECUTION_DESCRIPTION)
                           ),
        ]
        return lists.HeaderContentList(items,
                                       lists.Format(lists.ListType.ORDERED_LIST,
                                                    custom_separations=docs.SEPARATION_OF_HEADER_AND_CONTENTS)
                                       )


def _see_also_targets() -> List[see_also.SeeAlsoTarget]:
    return [
        concepts.PREPROCESSOR_CONCEPT_INFO.cross_reference_target,
        concepts.DIRECTIVE_CONCEPT_INFO.cross_reference_target,
        concepts.INSTRUCTION_CONCEPT_INFO.cross_reference_target,
        concepts.SYMBOL_CONCEPT_INFO.cross_reference_target,
    ]


BEFORE_STEP_LIST = """\
Test case file "processing" starts after the command line arguments have been parsed,
and {program_name} has been told to run a test case.


A test case file is processed in a number of steps,
where the actual execution of the test is the last step.


The outcome is reported by an exit code and an identifier printed as a single line on stdout.


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

PURPOSE_OF_SYNTAX_CHECKING = """\
Checks the syntax of all elements in the test case file
-
phases,
their {instructions},
and the {ATC} of the {act_phase:syntax} phase.


Processes {directive:s} ({including}).
"""

FAILURE_CONDITION_OF_SYNTAX_CHECKING = """\
Fails if {an_error_in_source} is found,
or if a {directive} fails.
"""

PURPOSE_OF_VALIDATION = """\
Checks references to {symbol:s} and external resources (files etc).
"""

FAILURE_CONDITION_OF_VALIDATION = """\
Fails if a reference to a {symbol}
that has not been defined or has invalid type,
is found,
or if a reference to a non-existing file is found, e.g.
"""

EXECUTION_DESCRIPTION = """\
Executes the actual test.
 
 
Executes the phases in the predefined order.


Executing a phase with {instructions} means executing all instructions
in the order they appear in the test case file.


The execution halts if an {instruction} encounters an error,
or, in the case of assertion instructions, if the
assertion fails. 
"""
