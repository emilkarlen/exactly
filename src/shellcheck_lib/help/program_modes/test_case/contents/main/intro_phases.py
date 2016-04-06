from shellcheck_lib.help.program_modes.test_case.contents.main.utils import Setup
from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCasePhaseDocumentation
from shellcheck_lib.util.textformat.parse import normalize_and_parse
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure import lists
from shellcheck_lib.util.textformat.structure.core import ParagraphItem
from shellcheck_lib.util.textformat.structure.structures import para, list_item, \
    simple_list_with_space_between_elements_and_content


def phases_documentation(setup: Setup) -> doc.SectionContents:
    paragraphs = normalize_and_parse(INTRO) + [phases_list_in_order_of_execution(setup)]
    return doc.SectionContents(paragraphs,
                               [])


INTRO = """\
Executing a test case means executing all of it's phases.


The phases are always executed in the same order,
regardless of the order they appear in the test case file.


The phases are (in order of execution):
"""


def phases_list_in_order_of_execution(setup: Setup) -> ParagraphItem:
    items = []
    for phase in setup.test_case_help.phase_helps_in_order_of_execution:
        assert isinstance(phase, TestCasePhaseDocumentation)
        items.append(list_item(phase.name.syntax,
                               [para(phase.purpose().single_line_description)]))
    return simple_list_with_space_between_elements_and_content(
        items,
        lists.ListType.VARIABLE_LIST)
