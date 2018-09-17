from exactly_lib.help.program_modes.test_case.contents.specification import file_syntax, intro, \
    environment as env_doc, structure
from exactly_lib.help.program_modes.test_case.contents.specification import outcome
from exactly_lib.help.program_modes.test_case.contents.specification import processing as processing
from exactly_lib.help.program_modes.test_case.contents.specification.utils import Setup
from exactly_lib.help.program_modes.test_case.contents_structure.test_case_help import TestCaseHelp
from exactly_lib.util.textformat.construction.section_contents_constructor import SectionContentsConstructor
from exactly_lib.util.textformat.construction.section_hierarchy import structures, hierarchy
from exactly_lib.util.textformat.construction.section_hierarchy.as_section_contents import \
    SectionContentsConstructorFromHierarchyGenerator
from exactly_lib.util.textformat.construction.section_hierarchy.hierarchy import Node, leaf

ONE_LINE_DESCRIPTION = "Executes a program in a temporary sandbox directory and checks it's result."


def generator(header: str,
              test_case_help: TestCaseHelp
              ) -> structures.SectionHierarchyGenerator:
    setup = Setup(test_case_help)
    return hierarchy.parent(
        header,
        [],
        [
            Node('introduction', leaf('Introduction', intro.Documentation())),
            Node('structure', structure.hierarchy_root('Structure', setup)),
            Node('exe-env', env_doc.hierarchy_root('Execution environment')),
            Node('file-syntax', file_syntax.generator('File syntax', setup)),
            Node('processing', leaf('Processing steps', processing.ContentsConstructor(setup))),
            Node('outcome', outcome.hierarchy_generator('Outcome', setup)),
        ])


def as_section_contents_constructor(test_case_help: TestCaseHelp) -> SectionContentsConstructor:
    return SectionContentsConstructorFromHierarchyGenerator(generator('unused header', test_case_help))
