from shellcheck_lib.cli.execution_mode.help.mode.main_program.contents import test_case_overview_help, \
    help_invokation_variants
from shellcheck_lib.cli.execution_mode.help.mode.main_program.help_request import MainProgramHelpRequest, \
    MainProgramHelpItem
from shellcheck_lib.util.textformat.structure import document as doc


class MainProgramHelpRenderer:
    def render(self, request: MainProgramHelpRequest):
        item = request.item
        if item is MainProgramHelpItem.PROGRAM:
            return doc.SectionContents(test_case_overview_help, [])
        if item is MainProgramHelpItem.HELP:
            pi = help_invokation_variants()
            return doc.SectionContents([pi], [])
        raise ValueError('Invalid %s: %s' % (str(MainProgramHelpItem), str(item)))
