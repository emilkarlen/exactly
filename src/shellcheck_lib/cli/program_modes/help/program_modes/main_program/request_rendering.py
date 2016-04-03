from shellcheck_lib.cli.program_modes.help.program_modes.main_program.help_request import MainProgramHelpRequest, \
    MainProgramHelpItem
from shellcheck_lib.help.program_modes.main_program.contents_structure import MainProgramHelp
from shellcheck_lib.help.utils.render import SectionContentsRenderer


class MainProgramHelpRendererResolver:
    def __init__(self, main_program_help: MainProgramHelp):
        self.main_program_help = main_program_help

    def renderer_for(self, request: MainProgramHelpRequest) -> SectionContentsRenderer:
        from shellcheck_lib.help.program_modes.main_program import render
        item = request.item
        if item is MainProgramHelpItem.PROGRAM:
            return render.OverviewRenderer()
        if item is MainProgramHelpItem.HELP:
            return render.InvokationVariantsRenderer()
        raise ValueError('Invalid %s: %s' % (str(MainProgramHelpItem), str(item)))
