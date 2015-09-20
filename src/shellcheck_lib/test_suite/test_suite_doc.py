from shellcheck_lib.document.model import PhaseContents, ElementType
from shellcheck_lib.test_suite.instruction_set.sections.anonymous import AnonymousSectionInstruction
from shellcheck_lib.test_suite.instruction_set.sections.cases import TestCaseSectionInstruction
from shellcheck_lib.test_suite.instruction_set.sections.suites import TestSuiteSectionInstruction


class TestSuite(tuple):
    def __new__(cls,
                anonymous_section: PhaseContents,
                suites_section: PhaseContents,
                cases_section: PhaseContents):
        TestSuite.__assert_instruction_class(anonymous_section,
                                             AnonymousSectionInstruction)
        TestSuite.__assert_instruction_class(suites_section,
                                             TestSuiteSectionInstruction)
        TestSuite.__assert_instruction_class(cases_section, TestCaseSectionInstruction)
        return tuple.__new__(cls, (anonymous_section,
                                   suites_section,
                                   cases_section))

    @property
    def anonymous_section(self) -> PhaseContents:
        return self[0]

    @property
    def suites_section(self) -> PhaseContents:
        return self[1]

    @property
    def cases_section(self) -> PhaseContents:
        return self[2]

    @staticmethod
    def __assert_instruction_class(phase_contents: PhaseContents,
                                   instruction_class):
        for element in phase_contents.elements:
            if element.element_type is ElementType.INSTRUCTION:
                assert isinstance(element.instruction, instruction_class)
