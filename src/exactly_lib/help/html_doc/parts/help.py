from exactly_lib.help.program_modes.help.cli_syntax import HelpCliSyntaxDocumentation
from exactly_lib.help.render.cli_program import \
    ProgramDocumentationSectionContentsConstructor
from exactly_lib.util.textformat.section_target_hierarchy import hierarchies as h


def root(header: str) -> h.SectionHierarchyGenerator:
    return h.leaf(header,
                  ProgramDocumentationSectionContentsConstructor(HelpCliSyntaxDocumentation()))
