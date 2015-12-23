from shellcheck_lib.cli.execution_mode.help.contents import ApplicationHelp, MainProgramHelp, \
    TestCaseHelp, TestSuiteHelp, TestCasePhaseHelp, TestCasePhaseInstructionSet, TestSuiteSectionHelp
from shellcheck_lib.execution import phases
from shellcheck_lib.test_case.help.config import phase_help_name
from shellcheck_lib.test_case.instruction_setup import InstructionsSetup
from shellcheck_lib.test_suite.parser import SECTION_NAME__SUITS, SECTION_NAME__CASES


def application_help_for(instructions_setup: InstructionsSetup) -> ApplicationHelp:
    return ApplicationHelp(MainProgramHelp(),
                           TestCaseHelp(phase_helps_for(instructions_setup)),
                           TestSuiteHelp([
                               TestSuiteSectionHelp(SECTION_NAME__SUITS),
                               TestSuiteSectionHelp(SECTION_NAME__CASES),
                           ]))


def phase_helps_for(instructions_setup: InstructionsSetup) -> iter:
    return [
        TestCasePhaseHelp(phase_help_name(phases.ANONYMOUS),
                          instruction_set_help(instructions_setup.config_instruction_set.values())),
        TestCasePhaseHelp(phase_help_name(phases.SETUP),
                          instruction_set_help(instructions_setup.setup_instruction_set.values())),
        TestCasePhaseHelp(phase_help_name(phases.ACT),
                          None),
        TestCasePhaseHelp(phase_help_name(phases.ASSERT),
                          instruction_set_help(instructions_setup.assert_instruction_set.values())),
        TestCasePhaseHelp(phase_help_name(phases.CLEANUP),
                          instruction_set_help(instructions_setup.cleanup_instruction_set.values())),
    ]


def instruction_set_help(single_instruction_setup_list: iter) -> TestCasePhaseInstructionSet:
    return TestCasePhaseInstructionSet(map(lambda x: x.description, single_instruction_setup_list))
