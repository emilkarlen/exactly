from exactly_lib.document.model import PhaseContents, ElementType
from exactly_lib.test_suite.instruction_set.sections.cases import TestCaseSectionInstruction
from exactly_lib.test_suite.instruction_set.sections.configuration import ConfigurationSectionInstruction
from exactly_lib.test_suite.instruction_set.sections.suites import TestSuiteSectionInstruction


class TestSuiteDocument(tuple):
    def __new__(cls,
                configuration_section: PhaseContents,
                suites_section: PhaseContents,
                cases_section: PhaseContents):
        TestSuiteDocument.__assert_instruction_class(configuration_section,
                                                     ConfigurationSectionInstruction)
        TestSuiteDocument.__assert_instruction_class(suites_section,
                                                     TestSuiteSectionInstruction)
        TestSuiteDocument.__assert_instruction_class(cases_section, TestCaseSectionInstruction)
        return tuple.__new__(cls, (configuration_section,
                                   suites_section,
                                   cases_section))

    @property
    def configuration_section(self) -> PhaseContents:
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
