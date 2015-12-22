import os
import shutil

from shellcheck_lib.cli.execution_mode.help.settings import HelpSettings, TestCaseHelpSettings, TestCaseHelpItem, \
    TestSuiteHelpSettings, TestSuiteHelpItem, ProgramHelpSettings
from shellcheck_lib.execution import phase_step
from shellcheck_lib.general.std import StdOutputFiles
from shellcheck_lib.general.textformat.formatting import section, paragraph_item
from shellcheck_lib.general.textformat.formatting.wrapper import Wrapper
from shellcheck_lib.general.textformat.structure import document as doc
from shellcheck_lib.general.textformat.structure.paragraph import para
from shellcheck_lib.test_case.help.instruction_description import DescriptionWithConstantValues
from shellcheck_lib.test_case.instruction_setup import InstructionsSetup


class TestCaseHelp:
    def overview(self, instruction_setup: InstructionsSetup) -> doc.SectionContents:
        return doc.SectionContents([para('TODO: test case overview help')], [])

    def phase(self, name: str) -> doc.SectionContents:
        return doc.SectionContents([para('TODO test-case help for phase ' + name)], [])

    def instruction_set(self, instruction_setup: InstructionsSetup) -> doc.SectionContents:
        return doc.SectionContents([para('TODO: instruction set help')], [])

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


class PrintInstructionsPerPhase:
    def __init__(self,
                 output: StdOutputFiles):
        self._std = output

    def apply(self, instruction_setup: InstructionsSetup):
        self._print_phase(phase_step.ANONYMOUS, instruction_setup.config_instruction_set)
        self._print_phase(phase_step.SETUP, instruction_setup.setup_instruction_set)
        self._print_phase(phase_step.ASSERT, instruction_setup.assert_instruction_set)
        self._print_phase(phase_step.CLEANUP, instruction_setup.cleanup_instruction_set)

    def _print_phase(self,
                     phase_name: str,
                     instruction_set: dict):
        if not instruction_set:
            return
        self._writeln(phase_name)
        for instruction_name, instruction_setup in instruction_set.items():
            self._writeln(instruction_name + ' : ' + instruction_setup.description.single_line_description)

    def _writeln(self, s: str):
        self._std.out.write(s)
        self._std.out.write(os.linesep)
