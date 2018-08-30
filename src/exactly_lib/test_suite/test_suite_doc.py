from exactly_lib.section_document.model import SectionContents, ElementType, new_empty_section_contents
from exactly_lib.test_suite.case_instructions import CaseSetupPhaseInstruction
from exactly_lib.test_suite.instruction_set.sections.cases import CaseSectionInstruction
from exactly_lib.section_document.model import SectionContents, ElementType
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionInstruction
from exactly_lib.test_suite.instruction_set.sections.suites import SuitesSectionInstruction


class TestSuiteDocument(tuple):
    def __new__(cls,
                configuration_section: SectionContents,
                suites_section: SectionContents,
                cases_section: SectionContents,
                case_configuration_phase: SectionContents,
                case_setup_phase: SectionContents,
                case_before_assert_phase: SectionContents,
                case_assert_phase: SectionContents,
                case_cleanup_phase: SectionContents,
                ):
        _assert_instruction_class(configuration_section,
                                  ConfigurationSectionInstruction)
        _assert_instruction_class(suites_section,
                                  SuitesSectionInstruction)
        _assert_instruction_class(cases_section,
                                  CaseSectionInstruction)

        _assert_instruction_class(case_configuration_phase,
                                  ConfigurationPhaseInstruction)
        _assert_instruction_class(case_setup_phase,
                                  SetupPhaseInstruction)
        _assert_instruction_class(case_before_assert_phase,
                                  BeforeAssertPhaseInstruction)
        _assert_instruction_class(case_assert_phase,
                                  AssertPhaseInstruction)
        _assert_instruction_class(case_cleanup_phase,
                                  CleanupPhaseInstruction)

        return tuple.__new__(cls, (configuration_section,
                                   suites_section,
                                   cases_section,
                                   case_configuration_phase,
                                   case_setup_phase,
                                   case_before_assert_phase,
                                   case_assert_phase,
                                   case_cleanup_phase))

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
    def case_configuration_phase(self) -> SectionContents:
        return self[3]

    @property
    def case_setup_phase(self) -> SectionContents:
        return self[4]

    @property
    def case_before_assert_phase(self) -> SectionContents:
        return self[5]

    @property
    def case_assert_phase(self) -> SectionContents:
        return self[6]

    @property
    def case_cleanup_phase(self) -> SectionContents:
        return self[7]


def _assert_instruction_class(phase_contents: SectionContents,
                              instruction_class):
    for element in phase_contents.elements:
        if element.element_type is ElementType.INSTRUCTION:
            assert isinstance(element.instruction_info.instruction, instruction_class)
