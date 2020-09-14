from typing import List

from exactly_lib import program_info
from exactly_lib.cli.definitions.program_modes.test_case.command_line_options import OPTION_FOR_PREPROCESSOR
from exactly_lib.definitions import formatting, misc_texts, processing
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import concepts, directives
from exactly_lib.definitions.test_case import phase_infos, phase_names
from exactly_lib.help.program_modes.test_case.contents.specification.utils import \
    step_with_single_exit_value, step_with_multiple_exit_values
from exactly_lib.help.render import see_also
from exactly_lib.processing import exit_values
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import \
    SectionContentsConstructor
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.textformat_parser import TextParser


class ContentsConstructor(SectionContentsConstructor):
    def __init__(self):
        self._tp = TextParser({
            'phase': phase_names.PHASE_NAME_DICTIONARY,
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'instruction': concepts.INSTRUCTION_CONCEPT_INFO.name,
            'ATC': concepts.ACTION_TO_CHECK_CONCEPT_INFO.singular_name,
            'symbol': concepts.SYMBOL_CONCEPT_INFO.name,
            'directive': concepts.DIRECTIVE_CONCEPT_INFO.name,
            'actor': concepts.ACTOR_CONCEPT_INFO.name,
            'exit_code': misc_texts.EXIT_CODE,
            'exit_identifier': misc_texts.EXIT_IDENTIFIER,
            'act_phase': phase_infos.ACT.name,
            'cli_option_for_preprocessor': formatting.cli_option(OPTION_FOR_PREPROCESSOR),
            'an_error_in_source': misc_texts.SYNTAX_ERROR_NAME.singular_determined,
            'including': formatting.keyword(directives.INCLUDING_DIRECTIVE_INFO.singular_name),

            'stdout': misc_texts.STDOUT,

            'execution': processing.STEP_EXECUTION,
            'validation': processing.STEP_VALIDATION,
            'preprocessing': processing.STEP_PRE_PROCESSING,
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
            docs.list_item(processing.STEP_PRE_PROCESSING.singular.capitalize(),
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
                                   NameAndValue('Syntax error',
                                                exit_values.NO_EXECUTION__SYNTAX_ERROR),
                                   NameAndValue('File inclusion error',
                                                exit_values.NO_EXECUTION__FILE_ACCESS_ERROR),
                               ],
                           )
                           ),
            docs.list_item(self._tp.text('{validation:/u} and syntax checking of {act_phase:syntax}'),
                           step_with_multiple_exit_values(
                               self._tp.fnap(PURPOSE_OF_VALIDATION),
                               self._tp.fnap(FAILURE_CONDITION_OF_VALIDATION),
                               [
                                   NameAndValue(self._tp.text('Invalid syntax of {act_phase:syntax}'),
                                                exit_values.EXECUTION__SYNTAX_ERROR),
                                   NameAndValue(self._tp.text('Invalid reference to {symbol} or external resource'),
                                                exit_values.EXECUTION__VALIDATION_ERROR),
                               ],
                           )
                           ),
            docs.list_item(processing.STEP_EXECUTION.singular.capitalize(),
                           self._tp.fnap(EXECUTION_DESCRIPTION)
                           ),
        ]
        return lists.HeaderContentList(items,
                                       lists.Format(lists.ListType.ORDERED_LIST,
                                                    custom_separations=docs.SEPARATION_OF_HEADER_AND_CONTENTS)
                                       )


def _see_also_targets() -> List[see_also.SeeAlsoTarget]:
    return cross_reference_id_list([
        concepts.PREPROCESSOR_CONCEPT_INFO,
        concepts.DIRECTIVE_CONCEPT_INFO,
        concepts.INSTRUCTION_CONCEPT_INFO,
        concepts.ACTOR_CONCEPT_INFO,
        concepts.SYMBOL_CONCEPT_INFO,
    ])


BEFORE_STEP_LIST = """\
Test case file "processing" starts after the command line arguments have been parsed,
and {program_name} has been told to run a test case.


A test case file is processed in a number of steps,
where the actual execution of the test is the last step.


The outcome is reported by {exit_code:a} and {exit_identifier:a} printed as a single line on {stdout}.
"""

PURPOSE_OF_PREPROCESSING = """\
Transforms the test case file.


This step is applied only if a preprocessor has been given by {cli_option_for_preprocessor},
or set in a test suite.
"""

FAILURE_CONDITION_OF_PREPROCESSING = """\
Fails if the preprocessor program cannot be executed, 
or if it exits with a non-zero {exit_code}.
"""

PURPOSE_OF_SYNTAX_CHECKING = """\
Checks the syntax of all elements in the test case file,
except for the {act_phase:syntax} phase.


Processes {directive:s} ({including}).
"""

FAILURE_CONDITION_OF_SYNTAX_CHECKING = """\
Fails if {an_error_in_source} is found,
or if a {directive} fails.
"""

PURPOSE_OF_VALIDATION = """\
Checks references to {symbol:s} and external resources (files),

and syntax of the {act_phase:syntax} phase
(according to the configured {actor}).
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


Executing a phase with {instruction:s} means executing all {instruction:s}
in the order they appear in the test case file.


{execution:/u} halts if an {instruction} encounters an error,
or, in the case of assertion {instruction:s}, if the
assertion fails. 
"""
