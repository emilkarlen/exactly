from . import instruction
from shellcheck_lib.document.model import PhaseContents


class TestSuite(tuple):
    def __new__(cls,
                suites_section: PhaseContents,
                cases_section: PhaseContents):
        TestSuite.__assert_instruction_class(suites_section, instruction.TestSuiteSectionInstruction)
        TestSuite.__assert_instruction_class(cases_section, instruction.TestCaseSectionInstruction)
        return tuple.__new__(cls, (suites_section,
                                   cases_section))

    @property
    def suites_section(self) -> PhaseContents:
        return self[0]

    @property
    def cases_section(self) -> PhaseContents:
        return self[1]

    @staticmethod
    def __assert_instruction_class(phase_contents: PhaseContents,
                                   instruction_class):
        for element in phase_contents.elements:
            if element.is_instruction:
                assert isinstance(element.instruction, instruction_class)
