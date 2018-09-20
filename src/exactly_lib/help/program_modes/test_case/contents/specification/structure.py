from exactly_lib.definitions.test_case import phase_names_plain
from exactly_lib.definitions.test_suite import file_names
from exactly_lib.help.program_modes.common.renderers import sections_short_list
from exactly_lib.help.program_modes.test_case.contents.specification.utils import Setup
from exactly_lib.test_case import phase_identifier
from exactly_lib.util.textformat.constructor import sections
from exactly_lib.util.textformat.section_target_hierarchy import hierarchies as h, generator
from exactly_lib.util.textformat.structure.structures import *
from exactly_lib.util.textformat.textformat_parser import TextParser


def root(header: str, setup: Setup) -> generator.SectionHierarchyGenerator:
    tp = TextParser({
        'default_suite_file_name': file_names.DEFAULT_SUITE_FILE
    })

    def const_paragraphs(header: str, paragraphs: List[ParagraphItem]) -> generator.SectionHierarchyGenerator:
        return h.leaf(header,
                      sections.constant_contents(section_contents(paragraphs)))

    def phases_documentation() -> List[ParagraphItem]:
        return (tp.fnap(_PHASES_INTRO) +
                [sections_short_list(setup.test_case_help.phase_helps_in_order_of_execution,
                                     phase_identifier.DEFAULT_PHASE.section_name,
                                     phase_names_plain.SECTION_CONCEPT_NAME)])

    return h.hierarchy(
        header,
        children=[
            h.child('phases',
                    const_paragraphs('Phases',
                                     phases_documentation())
                    ),
            h.child('suite-contents',
                    const_paragraphs('Inclusion of phase contents from test suites',
                                     tp.fnap(_SUITE_CONTENTS_INCLUSION))
                    ),
            h.child('part-of-suite',
                    const_paragraphs('Part of suite',
                                     tp.fnap(_PART_OF_SUITE))
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

_PART_OF_SUITE = """\
A test case is considered part of a suite, depending on how it is run.


When run in the following ways, it is part of a suite:

    
  * Standalone
  
      * A suite file is given via command line arguments
      
      * A file "{default_suite_file_name}" exits in the same directory as the test case file
      
        The file "{default_suite_file_name}" must be a test suite.
        
        
        Note that the test case file need not be listed in "{default_suite_file_name}".

  * Via test suite
  
    The test case file is listed in the suite.
"""
