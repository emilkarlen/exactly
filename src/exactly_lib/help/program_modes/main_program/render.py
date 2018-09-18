from exactly_lib.help.program_modes.main_program.contents import MainCliSyntaxDocumentation
from exactly_lib.help.render.cli_program import \
    ProgramDocumentationSectionContentsConstructor
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import \
    SectionContentsConstructor
from exactly_lib.util.textformat.structure import document as doc


class OverviewConstructor(SectionContentsConstructor):
    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        renderer = ProgramDocumentationSectionContentsConstructor(MainCliSyntaxDocumentation())
        return renderer.apply(environment)
