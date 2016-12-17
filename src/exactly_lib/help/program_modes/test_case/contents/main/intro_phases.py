from exactly_lib.help.program_modes.common.renderers import sections_short_list
from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup
from exactly_lib.test_case import phase_identifier
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import document as doc


def phases_documentation(setup: Setup) -> doc.SectionContents:
    paragraphs = (normalize_and_parse(INTRO) +
                  [sections_short_list(setup.test_case_help.phase_helps_in_order_of_execution,
                                       phase_identifier.DEFAULT_PHASE.section_name,
                                       phase_identifier.SECTION_CONCEPT_NAME)])
    return doc.SectionContents(paragraphs,
                               [])


INTRO = """\
Executing a test case means executing all of it's phases.


The phases are (in order of execution):
"""
