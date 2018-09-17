from exactly_lib.help.program_modes.help.cli_syntax import HelpCliSyntaxDocumentation
from exactly_lib.help.render.cli_program import \
    ProgramDocumentationSectionContentsConstructor
from exactly_lib.util.textformat.construction.section_hierarchy.generator import SectionHierarchyGenerator
from exactly_lib.util.textformat.construction.section_hierarchy.hierarchy import leaf


def generator(header: str) -> SectionHierarchyGenerator:
    return leaf(header,
                ProgramDocumentationSectionContentsConstructor(HelpCliSyntaxDocumentation()))
