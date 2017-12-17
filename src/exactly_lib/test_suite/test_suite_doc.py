from exactly_lib.section_document.model import SectionContents, ElementType, new_empty_section_contents
from exactly_lib.test_suite.case_instructions import CaseSetupPhaseInstruction
from exactly_lib.test_suite.instruction_set.sections.cases import TestCaseSectionInstruction
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionInstruction
from exactly_lib.test_suite.instruction_set.sections.suites import TestSuiteSectionInstruction


def _assert_instruction_class(phase_contents: SectionContents,
                              instruction_class):
    for element in phase_contents.elements:
        if element.element_type is ElementType.INSTRUCTION:
            assert isinstance(element.instruction_info.instruction, instruction_class)


class TestCaseInstructionSetupFromSuite(tuple):
    def __new__(cls, setup_section: SectionContents):
        _assert_instruction_class(setup_section,
                                  CaseSetupPhaseInstruction)
        return tuple.__new__(cls, (setup_section,))

    @property
    def setup_section(self) -> SectionContents:
        return self[0]


def empty_test_case_instruction_setup_from_suite() -> TestCaseInstructionSetupFromSuite:
    return TestCaseInstructionSetupFromSuite(new_empty_section_contents())


class TestSuiteDocument(tuple):
    def __new__(cls,
                configuration_section: SectionContents,
                suites_section: SectionContents,
                cases_section: SectionContents,
                case_setup: TestCaseInstructionSetupFromSuite
                ):
        _assert_instruction_class(configuration_section,
                                  ConfigurationSectionInstruction)
        _assert_instruction_class(suites_section,
                                  TestSuiteSectionInstruction)
        _assert_instruction_class(cases_section,
                                  TestCaseSectionInstruction)
        return tuple.__new__(cls, (configuration_section,
                                   suites_section,
                                   cases_section,
                                   case_setup))

    @property
    def configuration_section(self) -> SectionContents:
        return self[0]

    @property
    def suites_section(self) -> SectionContents:
        return self[1]

    @property
    def cases_section(self) -> SectionContents:
        return self[2]

    @property
    def case_setup(self) -> TestCaseInstructionSetupFromSuite:
        return self[3]
