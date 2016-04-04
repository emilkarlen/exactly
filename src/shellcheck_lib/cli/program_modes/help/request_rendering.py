import os
import shutil

from shellcheck_lib.cli.program_modes.help.concepts.help_request import ConceptHelpRequest
from shellcheck_lib.cli.program_modes.help.concepts.request_rendering import ConceptHelpRequestRendererResolver
from shellcheck_lib.cli.program_modes.help.program_modes.help_request import *
from shellcheck_lib.cli.program_modes.help.program_modes.main_program.help_request import MainProgramHelpRequest
from shellcheck_lib.cli.program_modes.help.program_modes.main_program.request_rendering import \
    MainProgramHelpRendererResolver
from shellcheck_lib.cli.program_modes.help.program_modes.test_case.help_request import TestCaseHelpRequest
from shellcheck_lib.cli.program_modes.help.program_modes.test_case.request_rendering import TestCaseHelpRendererResolver
from shellcheck_lib.cli.program_modes.help.program_modes.test_suite.help_request import TestSuiteHelpRequest
from shellcheck_lib.cli.program_modes.help.program_modes.test_suite.request_rendering import \
    TestSuiteHelpRendererResolver
from shellcheck_lib.help.contents_structure import ApplicationHelp
from shellcheck_lib.help.utils.render import SectionContentsRenderer
from shellcheck_lib.util.textformat.formatting import section, paragraph_item
from shellcheck_lib.util.textformat.formatting import text
from shellcheck_lib.util.textformat.formatting.lists import list_formats_with
from shellcheck_lib.util.textformat.formatting.wrapper import Wrapper
from shellcheck_lib.util.textformat.structure import core


def print_help(file,
               application_help: ApplicationHelp,
               help_request: HelpRequest):
    renderer = _renderer(application_help, help_request)
    page_width = shutil.get_terminal_size().columns
    formatter = _formatter(page_width)
    lines = formatter.format_section_contents(renderer.apply())
    for line in lines:
        file.write(line)
        file.write(os.linesep)


def _formatter(page_width):
    text_formatter = text.TextFormatter(HelpCrossReferenceFormatter())
    return section.Formatter(paragraph_item.Formatter(text_formatter,
                                                      Wrapper(page_width=page_width),
                                                      list_formats=list_formats_with(indent_str='  ')),
                             section_content_indent_str='   ')


class HelpCrossReferenceFormatter(text.CrossReferenceFormatter):
    def apply(self, cross_reference: core.CrossReferenceText) -> str:
        return 'TODO ' + cross_reference.title


def _renderer(application_help: ApplicationHelp,
              request: HelpRequest) -> SectionContentsRenderer:
    if isinstance(request, MainProgramHelpRequest):
        resolver = MainProgramHelpRendererResolver(application_help.main_program_help)
        return resolver.renderer_for(request)
    if isinstance(request, ConceptHelpRequest):
        resolver = ConceptHelpRequestRendererResolver(application_help.concepts_help)
        return resolver.renderer_for(request)
    if isinstance(request, TestCaseHelpRequest):
        resolver = TestCaseHelpRendererResolver(application_help.test_case_help)
        return resolver.resolve(request)
    if isinstance(request, TestSuiteHelpRequest):
        resolver = TestSuiteHelpRendererResolver(application_help.test_suite_help)
        return resolver.resolve(request)
    raise ValueError('Invalid %s: %s' % (str(HelpRequest), str(type(request))))
