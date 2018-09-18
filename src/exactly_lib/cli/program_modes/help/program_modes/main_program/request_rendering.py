from exactly_lib.cli.program_modes.help.program_modes.main_program.help_request import MainProgramHelpRequest, \
    MainProgramHelpItem
from exactly_lib.help.program_modes.help.cli_syntax import HelpCliSyntaxDocumentation
from exactly_lib.help.program_modes.main_program.contents_structure import MainProgramHelp
from exactly_lib.help.render.cli_program import \
    ProgramDocumentationSectionContentsConstructor
from exactly_lib.util.textformat.constructor.section import \
    SectionContentsConstructor


class MainProgramHelpRendererResolver:
    def __init__(self, main_program_help: MainProgramHelp):
        self.main_program_help = main_program_help

    def renderer_for(self, request: MainProgramHelpRequest) -> SectionContentsConstructor:
        from exactly_lib.help.program_modes.main_program import render
        item = request.item
        if item is MainProgramHelpItem.PROGRAM:
            return render.OverviewConstructor()
        if item is MainProgramHelpItem.HELP:
            return ProgramDocumentationSectionContentsConstructor(HelpCliSyntaxDocumentation())
        raise ValueError('Invalid %s: %s' % (str(MainProgramHelpItem), str(item)))
