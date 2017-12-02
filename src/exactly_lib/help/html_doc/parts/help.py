from exactly_lib.help.program_modes.help.cli_syntax import HelpCliSyntaxDocumentation
from exactly_lib.help.utils.cli_program.cli_program_documentation_rendering import \
    ProgramDocumentationSectionContentsConstructor
from exactly_lib.help.utils.rendering.section_hierarchy_rendering import SectionHierarchyGenerator, leaf


def generator(header: str) -> SectionHierarchyGenerator:
    return leaf(header,
                ProgramDocumentationSectionContentsConstructor(HelpCliSyntaxDocumentation()))
