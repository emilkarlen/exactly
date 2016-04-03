import os
import shutil

from shellcheck_lib.cli.program_modes.help.concepts.help_request import ConceptHelpRequest
from shellcheck_lib.cli.program_modes.help.concepts.request_rendering import ConceptHelpRequestRendererResolver
from shellcheck_lib.cli.program_modes.help.program_modes.help_request import *
from shellcheck_lib.cli.program_modes.help.program_modes.main_program.help_request import MainProgramHelpRequest
from shellcheck_lib.cli.program_modes.help.program_modes.main_program.request_rendering import \
    MainProgramHelpRendererResolver
from shellcheck_lib.cli.program_modes.help.program_modes.test_case.help_request import TestCaseHelpRequest
from shellcheck_lib.cli.program_modes.help.program_modes.test_case.request_rendering import TestCaseHelpRenderer
from shellcheck_lib.cli.program_modes.help.program_modes.test_suite.help_request import TestSuiteHelpRequest
from shellcheck_lib.cli.program_modes.help.program_modes.test_suite.request_rendering import TestSuiteHelpRenderer
from shellcheck_lib.help.contents_structure import ApplicationHelp
from shellcheck_lib.util.textformat.formatting import section, paragraph_item
from shellcheck_lib.util.textformat.formatting.lists import list_formats_with
from shellcheck_lib.util.textformat.formatting.wrapper import Wrapper
from shellcheck_lib.util.textformat.structure import document as doc


def doc_for(application_help: ApplicationHelp,
            request: HelpRequest) -> doc.SectionContents:
    if isinstance(request, MainProgramHelpRequest):
        resolver = MainProgramHelpRendererResolver(application_help.main_program_help)
        return resolver.renderer_for(request).apply()
    if isinstance(request, ConceptHelpRequest):
        resolver = ConceptHelpRequestRendererResolver(application_help.concepts_help)
        return resolver.renderer_for(request).apply()
    if isinstance(request, TestCaseHelpRequest):
        renderer = TestCaseHelpRenderer(application_help.test_case_help)
        return renderer.render(request)
    if isinstance(request, TestSuiteHelpRequest):
        renderer = TestSuiteHelpRenderer(application_help.test_suite_help)
        return renderer.render(request)
    raise ValueError('Invalid %s: %s' % (str(HelpRequest), str(type(request))))


def print_help(file,
               application_help: ApplicationHelp,
               help_request: HelpRequest):
    section_contents = doc_for(application_help, help_request)
    page_width = shutil.get_terminal_size().columns
    formatter = section.Formatter(paragraph_item.Formatter(Wrapper(page_width=page_width),
                                                           list_formats=list_formats_with(indent_str='  ')),
                                  section_content_indent_str='   ')
    lines = formatter.format_section_contents(section_contents)
    contents = os.linesep.join(lines)
    file.write(contents + os.linesep)
