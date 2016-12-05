from exactly_lib.cli.program_modes.help.program_modes.main_program.help_request import MainProgramHelpRequest, \
    MainProgramHelpItem
from exactly_lib.help.program_modes.help.cli_syntax import HelpCliSyntaxDocumentation
from exactly_lib.help.program_modes.main_program.contents_structure import MainProgramHelp
from exactly_lib.help.utils.cli_program_documentation_rendering import ProgramDocumentationSectionContentsRenderer
from exactly_lib.help.utils.section_contents_renderer import SectionContentsRenderer


class MainProgramHelpRendererResolver:
    def __init__(self, main_program_help: MainProgramHelp):
        self.main_program_help = main_program_help

    def renderer_for(self, request: MainProgramHelpRequest) -> SectionContentsRenderer:
        from exactly_lib.help.program_modes.main_program import render
        item = request.item
        if item is MainProgramHelpItem.PROGRAM:
            return render.OverviewRenderer()
        if item is MainProgramHelpItem.HELP:
            return ProgramDocumentationSectionContentsRenderer(HelpCliSyntaxDocumentation())
        raise ValueError('Invalid %s: %s' % (str(MainProgramHelpItem), str(item)))
