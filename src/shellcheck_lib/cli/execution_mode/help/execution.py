import os
import shutil

from shellcheck_lib.cli.execution_mode.help.settings import HelpSettings, TestCaseHelpSettings, TestCaseHelpItem, \
    TestSuiteHelpSettings, TestSuiteHelpItem, ProgramHelpSettings
from shellcheck_lib.general.textformat.formatting import section, paragraph_item
from shellcheck_lib.general.textformat.formatting.wrapper import Wrapper
from shellcheck_lib.general.textformat.structure import document as doc
from shellcheck_lib.general.textformat.structure import lists
from shellcheck_lib.general.textformat.structure.core import Text
from shellcheck_lib.general.textformat.structure.paragraph import para
from shellcheck_lib.test_case.help.instruction_description import DescriptionWithConstantValues
from shellcheck_lib.test_case.instruction_setup import InstructionsSetup


class TestCaseHelp:
    def overview(self, instruction_setup: InstructionsSetup) -> doc.SectionContents:
        return doc.SectionContents([para('TODO: test case overview help')], [])

    def phase(self, name: str) -> doc.SectionContents:
        return doc.SectionContents([para('TODO test-case help for phase ' + name)], [])

    def instruction_set(self, instruction_setup: InstructionsSetup) -> doc.SectionContents:
        sections = []
        for (phase, instruction_set_dict) in instruction_setup.phase_and_instruction_set:
            instruction_list_items = []
            for (instruction_name, instruction_setup) in instruction_set_dict.items():
                description_para = para(instruction_setup.description.single_line_description())
                instruction_list_items.append(lists.HeaderValueListItem(Text(instruction_name),
                                                                        [description_para]))
            instruction_list = lists.HeaderValueList(lists.ListType.VARIABLE_LIST,
                                                     instruction_list_items)
            sections.append(doc.Section(Text(phase.identifier),
                                        doc.SectionContents([instruction_list], [])))
        return doc.SectionContents([], sections)

    def instruction(self, name: str, description: DescriptionWithConstantValues) -> doc.SectionContents:
        return doc.SectionContents([para('TODO test-case help for instruction ' + name)], [])


class TestSuiteHelp:
    def overview(self) -> doc.SectionContents:
        return doc.SectionContents([para('TODO: test suite overview help')], [])

    def section(self, name: str) -> doc.SectionContents:
        return doc.SectionContents([para('TODO suite help for section ' + name)], [])


def print_help(file,
               instruction_setup: InstructionsSetup,
               settings: HelpSettings):
    section_contents = doc_for(instruction_setup, settings)
    terminal_size = shutil.get_terminal_size()
    formatter = section.Formatter(paragraph_item.Formatter(Wrapper(page_width=terminal_size.columns)))
    lines = formatter.format_section_contents(section_contents)
    for line in lines:
        file.write(line)
        file.write(os.linesep)


def doc_for(instruction_setup: InstructionsSetup,
            settings: HelpSettings) -> doc.SectionContents:
    if isinstance(settings, ProgramHelpSettings):
        return doc.SectionContents([para('TODO program help')], [])
    if isinstance(settings, TestCaseHelpSettings):
        tc_help = TestCaseHelp()
        item = settings.item
        if item is TestCaseHelpItem.OVERVIEW:
            return tc_help.overview(instruction_setup)
        if item is TestCaseHelpItem.INSTRUCTION_SET:
            return tc_help.instruction_set(instruction_setup)
        if item is TestCaseHelpItem.PHASE:
            return tc_help.phase(settings.name)
        if item is TestCaseHelpItem.INSTRUCTION:
            return tc_help.instruction(settings.name, settings.instruction_description)
        raise ValueError('Invalid %s: %s' % (str(TestCaseHelpItem), str(item)))
    if isinstance(settings, TestSuiteHelpSettings):
        ts_help = TestSuiteHelp()
        item = settings.item
        if item is TestSuiteHelpItem.OVERVIEW:
            return ts_help.overview()
        if item is TestSuiteHelpItem.SECTION:
            return ts_help.section(settings.name)
        raise ValueError('Invalid %s: %s' % (str(TestSuiteHelpItem), str(item)))
    raise ValueError('Invalid %s: %s' % (str(HelpSettings), str(type(settings))))
