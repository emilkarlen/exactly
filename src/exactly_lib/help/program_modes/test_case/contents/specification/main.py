from exactly_lib.help.program_modes.test_case.contents.specification import file_syntax, intro, \
    environment as env_doc, structure
from exactly_lib.help.program_modes.test_case.contents.specification import outcome
from exactly_lib.help.program_modes.test_case.contents.specification import processing as processing
from exactly_lib.help.program_modes.test_case.contents.specification.utils import Setup
from exactly_lib.help.program_modes.test_case.contents_structure.test_case_help import TestCaseHelp
from exactly_lib.util.textformat.constructor.section import \
    SectionContentsConstructor
from exactly_lib.util.textformat.section_target_hierarchy import hierarchies as h
from exactly_lib.util.textformat.section_target_hierarchy.as_section_contents import \
    SectionContentsConstructorFromHierarchyGenerator
from exactly_lib.util.textformat.section_target_hierarchy.generator import SectionHierarchyGenerator

ONE_LINE_DESCRIPTION = "Executes a program in a temporary sandbox directory and checks it's result."


def root(header: str,
         test_case_help: TestCaseHelp
         ) -> SectionHierarchyGenerator:
    setup = Setup(test_case_help)
    return h.hierarchy(
        header,
        children=[
            h.child('introduction', h.leaf('Introduction', intro.Documentation())),
            h.child('structure', structure.root('Structure', setup)),
            h.child('exe-env', env_doc.root('Execution environment')),
            h.child('file-syntax', file_syntax.root('File syntax', setup)),
            h.child('processing', h.leaf('Processing steps', processing.ContentsConstructor(setup))),
            h.child('outcome', outcome.root('Outcome', setup)),
        ])


def as_section_contents_constructor(test_case_help: TestCaseHelp) -> SectionContentsConstructor:
    return SectionContentsConstructorFromHierarchyGenerator(root('unused header', test_case_help))
