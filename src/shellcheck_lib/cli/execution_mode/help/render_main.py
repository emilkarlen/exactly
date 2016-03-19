import os
import shutil

from shellcheck_lib.cli.execution_mode.help.contents2 import help_invokation_variants, test_case_overview_help
from shellcheck_lib.cli.execution_mode.help.contents_structure import ApplicationHelp
from shellcheck_lib.cli.execution_mode.help.mode.help_request import *
from shellcheck_lib.cli.execution_mode.help.mode.main_program.help_request import MainProgramHelpItem, \
    MainProgramHelpRequest
from shellcheck_lib.cli.execution_mode.help.mode.test_case.help_request import TestCaseHelpRequest
from shellcheck_lib.cli.execution_mode.help.mode.test_case.render import TestCaseHelpRenderer
from shellcheck_lib.cli.execution_mode.help.mode.test_suite.help_request import TestSuiteHelpRequest
from shellcheck_lib.cli.execution_mode.help.mode.test_suite.render import TestSuiteHelpRenderer
from shellcheck_lib.util.textformat.formatting import section, paragraph_item
from shellcheck_lib.util.textformat.formatting.lists import list_formats_with
from shellcheck_lib.util.textformat.formatting.wrapper import Wrapper
from shellcheck_lib.util.textformat.structure import document as doc


def print_help(file,
               application_help: ApplicationHelp,
               settings: HelpRequest):
    section_contents = doc_for(application_help, settings)
    page_width = shutil.get_terminal_size().columns
    formatter = section.Formatter(paragraph_item.Formatter(Wrapper(page_width=page_width),
                                                           list_formats=list_formats_with(indent_str='  ')),
                                  section_content_indent_str='   ')
    lines = formatter.format_section_contents(section_contents)
    contents = os.linesep.join(lines)
    file.write(contents + os.linesep)


def doc_for(application_help: ApplicationHelp,
            request: HelpRequest) -> doc.SectionContents:
    if isinstance(request, MainProgramHelpRequest):
        item = request.item
        if item is MainProgramHelpItem.PROGRAM:
            return doc.SectionContents(test_case_overview_help, [])
        if item is MainProgramHelpItem.HELP:
            pi = help_invokation_variants()
            return doc.SectionContents([pi], [])
        raise ValueError('Invalid %s: %s' % (str(MainProgramHelpItem), str(item)))
    if isinstance(request, TestCaseHelpRequest):
        renderer = TestCaseHelpRenderer(application_help.test_case_help)
        return renderer.render(request)
    if isinstance(request, TestSuiteHelpRequest):
        renderer = TestSuiteHelpRenderer(application_help.test_suite_help)
        return renderer.render(request)
    raise ValueError('Invalid %s: %s' % (str(HelpRequest), str(type(request))))
