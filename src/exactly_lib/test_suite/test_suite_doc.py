from exactly_lib.section_document.model import SectionContents, ElementType
from exactly_lib.test_suite.instruction_set.sections.cases import TestCaseSectionInstruction
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import ConfigurationSectionInstruction
from exactly_lib.test_suite.instruction_set.sections.suites import TestSuiteSectionInstruction


class TestSuiteDocument(tuple):
    def __new__(cls,
                configuration_section: SectionContents,
                suites_section: SectionContents,
                cases_section: SectionContents):
        TestSuiteDocument.__assert_instruction_class(configuration_section,
                                                     ConfigurationSectionInstruction)
        TestSuiteDocument.__assert_instruction_class(suites_section,
                                                     TestSuiteSectionInstruction)
        TestSuiteDocument.__assert_instruction_class(cases_section,
                                                     TestCaseSectionInstruction)
        return tuple.__new__(cls, (configuration_section,
                                   suites_section,
                                   cases_section))

    @property
    def configuration_section(self) -> SectionContents:
        return self[0]

    @property
    def suites_section(self) -> SectionContents:
        return self[1]

    @property
    def cases_section(self) -> SectionContents:
        return self[2]

    @staticmethod
    def __assert_instruction_class(phase_contents: SectionContents,
                                   instruction_class):
        for element in phase_contents.elements:
            if element.element_type is ElementType.INSTRUCTION:
                assert isinstance(element.instruction, instruction_class)
