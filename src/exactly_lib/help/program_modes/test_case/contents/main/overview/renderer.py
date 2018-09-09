from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup
from exactly_lib.util.textformat.construction.section_hierarchy.hierarchy import leaf, parent, Node
from exactly_lib.util.textformat.construction.section_hierarchy.structures import \
    SectionHierarchyGenerator
from . import intro, environment as env_doc, phases, test_case


def generator(header: str, setup: Setup) -> SectionHierarchyGenerator:
    return parent(header, [],
                  [
                      Node('introduction', leaf('Introduction', intro.Documentation(setup))),
                      Node('test-cases', leaf('Test cases', test_case.Documentation(setup))),
                      Node('environment', leaf('Environment', env_doc.Documentation(setup))),
                      Node('phases', leaf('Phases', phases.Documentation(setup))),
                  ]
                  )
