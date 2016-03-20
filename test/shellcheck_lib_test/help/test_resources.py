from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCasePhaseInstructionSet, \
    TestCasePhaseHelp, TestCasePhaseHelpForPhaseWithInstructions
from shellcheck_lib.help.program_modes.test_case.instruction_documentation import InstructionDocumentation
from shellcheck_lib.help.utils.description import single_line_description
from shellcheck_lib_test.test_resources.instruction_description import InstructionDocumentationWithConstantValues


def instr_descr(phase_name: str, name: str) -> InstructionDocumentation:
    return InstructionDocumentationWithConstantValues(
        name,
        single_line_description_that_identifies_instruction_and_phase(phase_name,
                                                                      name),
        '',
        [])


def single_line_description_that_identifies_instruction_and_phase(phase_name: str,
                                                                  instruction_name: str) -> str:
    return phase_name + '/' + instruction_name


def test_case_phase_help(phase_name: str,
                         instruction_names: list) -> TestCasePhaseHelp:
    instruction_set = test_case_phase_instruction_set(phase_name, instruction_names)
    return TestCasePhaseHelpForPhaseWithInstructions(phase_name,
                                                     single_line_description(
                                                         'single_line_description for phase ' + phase_name),
                                                     instruction_set)


def test_case_phase_instruction_set(phase_name: str,
                                    instruction_names: list) -> TestCasePhaseInstructionSet:
    instruction_descriptions = map(lambda name: instr_descr(phase_name, name),
                                   instruction_names)
    return TestCasePhaseInstructionSet(instruction_descriptions)
