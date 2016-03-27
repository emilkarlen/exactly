from shellcheck_lib.cli.cli_environment.command_line_options import OPTION_FOR_PREPROCESSOR
from shellcheck_lib.help.program_modes.test_case.contents.main.setup import Setup
from shellcheck_lib.help.utils.formatting import AnyInstructionNameDictionary, cli_option
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure.structures import *


def test_case_processing_documentation(setup: Setup) -> doc.SectionContents:
    instruction_dict = AnyInstructionNameDictionary()
    preamble_paragraphs = [para('A test case file is processed in a number of steps:')]
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
                [para('If a preprocessor has been given by %s.' %
                      cli_option(OPTION_FOR_PREPROCESSOR))]),
            lists.HeaderContentListItem(
                text('syntax checking'),
                [para('Aborts the test case if a syntax error is found.')]),
            lists.HeaderContentListItem(
                text('validation'),
                [para('Aborts the test case if an unresolved file reference is found, e.g.')]),
            lists.HeaderContentListItem(
                text('execution'),
                [para('Outcome depends on the outcome of the {phase[assert]} phase.'.format(phase=setup.phase_names))]),
        ],
        lists.Format(lists.ListType.ORDERED_LIST,
                     custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS)
    )


"""
A test case file is processed by a sequence of steps:
preprocessing (if a preprocessor has been given)
syntax checking (aborting the test case if a syntax error is found)
validation (aborting the test case if an unresolved file reference is found, e.g.)
execution
"""
