import os
import shutil

from shellcheck_lib.cli.execution_mode.help.contents2 import help_invokation_variants, test_case_overview_help
from shellcheck_lib.cli.execution_mode.help.contents_structure import ApplicationHelp
from shellcheck_lib.cli.execution_mode.help.help_request import *
from shellcheck_lib.cli.execution_mode.help.mode.test_case.render import TestCaseHelpRenderer
from shellcheck_lib.cli.execution_mode.help.mode.test_suite.contents_structure import TestSuiteSectionHelp
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
            settings: HelpRequest) -> doc.SectionContents:
    if isinstance(settings, ProgramHelpRequest):
        item = settings.item
        if item is ProgramHelpItem.PROGRAM:
            return doc.SectionContents(test_case_overview_help, [])
        if item is ProgramHelpItem.HELP:
            pi = help_invokation_variants()
            return doc.SectionContents([pi], [])
        raise ValueError('Invalid %s: %s' % (str(ProgramHelpItem), str(item)))
    if isinstance(settings, TestCaseHelpRequest):
        tc_help = TestCaseHelpRenderer(application_help.test_case_help)
        return tc_help.render(settings)
    if isinstance(settings, TestSuiteHelpRequest):
        ts_help = TestSuiteHelpRenderer()
        item = settings.item
        if item is TestSuiteHelpItem.OVERVIEW:
            return ts_help.overview(application_help.test_suite_help)
        if item is TestSuiteHelpItem.SECTION:
            data = settings.data
            assert isinstance(data, TestSuiteSectionHelp)
            return ts_help.section(data)
        raise ValueError('Invalid %s: %s' % (str(TestSuiteHelpItem), str(item)))
    raise ValueError('Invalid %s: %s' % (str(HelpRequest), str(type(settings))))
