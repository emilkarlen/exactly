import os
import shutil

from shellcheck_lib.cli.execution_mode.help.contents import ApplicationHelp, TestSuiteHelp, \
    TestSuiteSectionHelp, TestCaseHelp, TestCasePhaseHelp
from shellcheck_lib.cli.execution_mode.help.render.test_case import instruction_set
from shellcheck_lib.cli.execution_mode.help.settings import HelpSettings, TestCaseHelpSettings, TestCaseHelpItem, \
    TestSuiteHelpSettings, TestSuiteHelpItem, ProgramHelpSettings
from shellcheck_lib.general.textformat.formatting import section, paragraph_item
from shellcheck_lib.general.textformat.formatting.wrapper import Wrapper
from shellcheck_lib.general.textformat.structure import document as doc
from shellcheck_lib.general.textformat.structure.core import Text
from shellcheck_lib.general.textformat.structure.paragraph import para
from shellcheck_lib.test_case.help.instruction_description import Description
from shellcheck_lib.test_case.help.render import instruction


class TestCaseHelpRenderer:
    def overview(self, test_case_help: TestCaseHelp) -> doc.SectionContents:
        return doc.SectionContents([para('TODO: test case overview help')], [])

    def phase(self, phase_help: TestCasePhaseHelp) -> doc.SectionContents:
        return doc.SectionContents([para('TODO test-case help for phase ' + phase_help.name)], [])

    def instruction_set(self, test_case_help: TestCaseHelp) -> doc.SectionContents:
        return instruction_set.instruction_set(test_case_help)

    def instruction(self, description: Description) -> doc.SectionContents:
        return instruction.instruction_man_page(description)

    def instruction_list(self,
                         instruction_name: str,
                         phase_and_instruction_description_list: list) -> doc.SectionContents:
        sections = []
        for phase_and_instruction_description in phase_and_instruction_description_list:
            man_page = self.instruction(phase_and_instruction_description[1])
            phase_section = doc.Section(Text(phase_and_instruction_description[0].identifier),
                                        man_page)
            sections.append(phase_section)
        initial_paragraphs = []
        if len(phase_and_instruction_description_list) > 1:
            initial_paragraphs = [para('"%s" is in multiple phases.' % instruction_name)]
        return doc.SectionContents(initial_paragraphs, sections)


class TestSuiteHelpRenderer:
    def overview(self,
                 suite_help: TestSuiteHelp) -> doc.SectionContents:
        return doc.SectionContents([para('TODO: test suite overview help')], [])

    def section(self, section_help: TestSuiteSectionHelp) -> doc.SectionContents:
        return doc.SectionContents([para('TODO suite help for section ' + section_help.name)], [])


def print_help(file,
               application_help: ApplicationHelp,
               settings: HelpSettings):
    section_contents = doc_for(application_help, settings)
    terminal_size = shutil.get_terminal_size()
    formatter = section.Formatter(paragraph_item.Formatter(Wrapper(page_width=terminal_size.columns)),
                                  section_content_indent_str=4 * ' ')
    lines = formatter.format_section_contents(section_contents)
    for line in lines:
        file.write(line)
        file.write(os.linesep)


def doc_for(application_help: ApplicationHelp,
            settings: HelpSettings) -> doc.SectionContents:
    if isinstance(settings, ProgramHelpSettings):
        return doc.SectionContents([para('TODO program help')], [])
    if isinstance(settings, TestCaseHelpSettings):
        tc_help = TestCaseHelpRenderer()
        item = settings.item
        if item is TestCaseHelpItem.OVERVIEW:
            return tc_help.overview(application_help.test_case_help)
        if item is TestCaseHelpItem.INSTRUCTION_SET:
            return tc_help.instruction_set(application_help.test_case_help)
        if item is TestCaseHelpItem.PHASE:
            return tc_help.phase(settings.data)
        if item is TestCaseHelpItem.INSTRUCTION:
            return tc_help.instruction(settings.data)
        if item is TestCaseHelpItem.INSTRUCTION_LIST:
            return tc_help.instruction_list(settings.name, settings.data)
        raise ValueError('Invalid %s: %s' % (str(TestCaseHelpItem), str(item)))
    if isinstance(settings, TestSuiteHelpSettings):
        ts_help = TestSuiteHelpRenderer()
        item = settings.item
        if item is TestSuiteHelpItem.OVERVIEW:
            return ts_help.overview(application_help.test_suite_help)
        if item is TestSuiteHelpItem.SECTION:
            data = settings.data
            assert isinstance(data, TestSuiteSectionHelp)
            return ts_help.section(data)
        raise ValueError('Invalid %s: %s' % (str(TestSuiteHelpItem), str(item)))
    raise ValueError('Invalid %s: %s' % (str(HelpSettings), str(type(settings))))
