from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.help.contents_structure import ApplicationHelp
from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet, \
    SectionDocumentation
from exactly_lib.help.program_modes.main_program.contents_structure import MainProgramHelp
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.structure.structures import para, text
from exactly_lib_test.common.test_resources.instruction_documentation import InstructionDocumentationWithConstantValues


def instr_descr(phase_name: str, name: str) -> InstructionDocumentation:
    return InstructionDocumentationWithConstantValues(
        name,
        single_line_description_that_identifies_instruction_and_section(phase_name,
                                                                        name),
        '',
        [])


def single_line_description_that_identifies_instruction_and_section(phase_name: str,
                                                                    instruction_name: str) -> str:
    return phase_name + '/' + instruction_name


def section_documentation(phase_name: str,
                          instruction_names: list,
                          is_mandatory: bool = False) -> SectionDocumentation:
    instruction_set = section_instruction_set(phase_name, instruction_names)
    return SectionDocumentationForSectionWithInstructionsTestImpl(phase_name,
                                                                  instruction_set,
                                                                  is_mandatory)


def section_instruction_set(section_name: str,
                            instruction_names: list) -> SectionInstructionSet:
    instruction_descriptions = map(lambda name: instr_descr(section_name, name),
                                   instruction_names)
    return SectionInstructionSet(instruction_descriptions)


def application_help_for(test_case_phase_helps: list,
                         suite_sections=(),
                         entity_name_2_entity_configuration: dict = None,
                         ) -> ApplicationHelp:
    return ApplicationHelp(MainProgramHelp(),
                           TestCaseHelp(test_case_phase_helps),
                           TestSuiteHelp(suite_sections),
                           {} if entity_name_2_entity_configuration is None else entity_name_2_entity_configuration)


def application_help_for_suite_sections(suite_sections: list) -> ApplicationHelp:
    return ApplicationHelp(MainProgramHelp(),
                           TestCaseHelp([]),
                           TestSuiteHelp(suite_sections),
                           {})


class SectionDocumentationForSectionWithoutInstructionsTestImpl(SectionDocumentation):
    def __init__(self, name: str):
        super().__init__(name)

    def purpose(self) -> Description:
        return Description(text('Single line purpose for phase ' + self.name.syntax),
                           [para('Rest of purpose for phase ' + self.name.syntax)])

    @property
    def has_instructions(self) -> bool:
        return False

    @property
    def instruction_set(self) -> SectionInstructionSet:
        raise NotImplementedError('This section does not have instructions.')


class SectionDocumentationForSectionWithInstructionsTestImpl(SectionDocumentation):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet,
                 is_mandatory: bool = False):
        super().__init__(name)
        self._instruction_set = instruction_set
        self._is_mandatory = is_mandatory

    def is_mandatory(self) -> bool:
        return self._is_mandatory

    def purpose(self) -> Description:
        return Description(text('Single line purpose for phase ' + self.name.syntax),
                           [para('Rest of purpose for phase ' + self.name.syntax)])

    @property
    def has_instructions(self) -> bool:
        return True

    @property
    def instruction_set(self) -> SectionInstructionSet:
        return self._instruction_set
