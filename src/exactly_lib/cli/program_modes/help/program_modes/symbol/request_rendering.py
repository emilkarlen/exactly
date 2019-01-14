from exactly_lib.cli.program_modes.help.program_modes.symbol.help_request import SymbolHelpRequest
from exactly_lib.help.program_modes.symbol.cli_syntax import SymbolCliSyntaxDocumentation
from exactly_lib.help.render.cli_program import \
    ProgramDocumentationSectionContentsConstructor
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import \
    SectionContentsConstructor
from exactly_lib.util.textformat.structure import document as doc


class SymbolHelpConstructorResolver:
    def resolve(self, request: SymbolHelpRequest) -> SectionContentsConstructor:
        return ProgramDocumentationSectionContentsConstructor(SymbolCliSyntaxDocumentation())

    def render(self, request: SymbolHelpRequest,
               environment: ConstructionEnvironment) -> doc.SectionContents:
        return self.resolve(request).apply(environment)
