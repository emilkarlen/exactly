from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCasePhaseInstructionSet, \
    TestCasePhaseHelp
from shellcheck_lib.help.program_modes.test_case.instruction_documentation import InstructionDocumentation
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure.paragraph import para
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
    return TestCasePhaseHelpForPhaseWithInstructionsTestImpl(phase_name,
                                                             instruction_set)


def test_case_phase_instruction_set(phase_name: str,
                                    instruction_names: list) -> TestCasePhaseInstructionSet:
    instruction_descriptions = map(lambda name: instr_descr(phase_name, name),
                                   instruction_names)
    return TestCasePhaseInstructionSet(instruction_descriptions)


class TestCasePhaseHelpForPhaseWithInstructionsTestImpl(TestCasePhaseHelp):
    def __init__(self,
                 name: str,
                 instruction_set: TestCasePhaseInstructionSet):
        super().__init__(name)
        self._instruction_set = instruction_set

    def render(self) -> doc.SectionContents:
        return doc.SectionContents([para('Rendition of phase "%s"' % self._name)],
                                   [])

    @property
    def is_phase_with_instructions(self) -> bool:
        return True

    @property
    def instruction_set(self) -> TestCasePhaseInstructionSet:
        return self._instruction_set
