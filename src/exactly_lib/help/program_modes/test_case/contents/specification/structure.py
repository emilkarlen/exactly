from exactly_lib.definitions.test_case import phase_names_plain
from exactly_lib.help.program_modes.common.renderers import sections_short_list
from exactly_lib.help.program_modes.test_case.contents.specification.utils import Setup
from exactly_lib.test_case import phase_identifier
from exactly_lib.util.textformat.construction.section_contents_constructor import constant_section_contents
from exactly_lib.util.textformat.construction.section_hierarchy import structures, hierarchy
from exactly_lib.util.textformat.construction.section_hierarchy.hierarchy import Node
from exactly_lib.util.textformat.structure.structures import *
from exactly_lib.util.textformat.textformat_parser import TextParser


def hierarchy_root(header: str, setup: Setup) -> structures.SectionHierarchyGenerator:
    tp = TextParser()

    def const_paragraphs(header: str, paragraphs: List[ParagraphItem]) -> structures.SectionHierarchyGenerator:
        return hierarchy.leaf(header,
                              constant_section_contents(section_contents(paragraphs)))

    def phases_documentation() -> List[ParagraphItem]:
        return (tp.fnap(_PHASES_INTRO) +
                [sections_short_list(setup.test_case_help.phase_helps_in_order_of_execution,
                                     phase_identifier.DEFAULT_PHASE.section_name,
                                     phase_names_plain.SECTION_CONCEPT_NAME)])

    return hierarchy.parent(
        header,
        [],
        [
            Node('phases',
                 const_paragraphs('Phases',
                                  phases_documentation())
                 ),
            Node('suite-contents',
                 const_paragraphs('Inclusion of phase contents from test suites',
                                  tp.fnap(_SUITE_CONTENTS_INCLUSION))
                 ),
        ]
    )


_PHASES_INTRO = """\
A test case contains a sequence of "phases".

Executing a test case means executing all of it's phases.


All phases are optional.


The phases are (in order of execution):
"""

_SUITE_CONTENTS_INCLUSION = """\
A test suite can contain test case contents.

When a test case is run as part of a suite, this contents is included in the case.
"""
