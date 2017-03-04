from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup
from exactly_lib.help.utils.section_hierarchy_rendering import parent, leaf, SectionGenerator
from . import intro, environment as env_doc, phases, test_case


def generator(header: str, setup: Setup) -> SectionGenerator:
    return parent(header, [],
                  [
                      ('introduction', leaf('Introduction', intro.Documentation(setup))),
                      ('test-cases', leaf('Test cases', test_case.Documentation(setup))),
                      ('environment', leaf('Environment', env_doc.Documentation(setup))),
                      ('phases', leaf('Phases', phases.Documentation(setup))),
                  ]
                  )
