from typing import Iterable, List, Sequence, Optional, Dict

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.definitions.cross_ref.concrete_cross_refs import CustomCrossReferenceId
from exactly_lib.definitions.section_info import SectionInfo
from exactly_lib.help.contents_structure.application import ApplicationHelp
from exactly_lib.help.contents_structure.entity import EntityTypeConfiguration
from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet, \
    SectionDocumentation
from exactly_lib.help.program_modes.main_program.contents_structure import MainProgramHelp
from exactly_lib.help.program_modes.test_case.contents_structure.test_case_help import TestCaseHelp
from exactly_lib.help.program_modes.test_suite.contents_structure.test_suite_help import TestSuiteHelp
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


def section_documentation(section_name: str,
                          instruction_names: List[str]) -> SectionDocumentation:
    instruction_set = section_instruction_set(section_name, instruction_names)
    return SectionDocumentationForSectionWithInstructionsTestImpl(section_name,
                                                                  instruction_set)


def section_instruction_set(section_name: str,
                            instruction_names: List[str]) -> SectionInstructionSet:
    instruction_descriptions = map(lambda name: instr_descr(section_name, name),
                                   instruction_names)
    return SectionInstructionSet(instruction_descriptions)


def application_help_for(test_case_phase_helps: Sequence[SectionDocumentation],
                         suite_sections: Sequence[SectionDocumentation] = (),
                         entity_name_2_entity_configuration: Optional[Dict[str, EntityTypeConfiguration]] = None,
                         ) -> ApplicationHelp:
    return ApplicationHelp(MainProgramHelp(),
                           TestCaseHelp(test_case_phase_helps),
                           TestSuiteHelp(suite_sections, []),
                           {} if entity_name_2_entity_configuration is None else entity_name_2_entity_configuration)


def application_help_for_suite_sections(suite_sections: Iterable[SectionDocumentation]) -> ApplicationHelp:
    return ApplicationHelp(MainProgramHelp(),
                           TestCaseHelp([]),
                           TestSuiteHelp(suite_sections, []),
                           {})


class SectionDocumentationForSectionWithoutInstructionsTestImpl(SectionDocumentation):
    def __init__(self, name: str):
        self._section_info = SectionInfoTestImpl(name)

    @property
    def section_info(self) -> SectionInfo:
        return self._section_info

    def purpose(self) -> Description:
        return Description(text('Single line purpose for phase ' + self.name.syntax),
                           [para('Rest of purpose for phase ' + self.name.syntax)])

    @property
    def has_instructions(self) -> bool:
        return False

    @property
    def instruction_set(self) -> Optional[SectionInstructionSet]:
        raise NotImplementedError('This section does not have instructions.')


class SectionDocumentationForSectionWithInstructionsTestImpl(SectionDocumentation):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        self._instruction_set = instruction_set
        self._section_info = SectionInfoWithoutInstructionsInfoTestImpl(name)

    @property
    def section_info(self) -> SectionInfo:
        return self._section_info

    def purpose(self) -> Description:
        return Description(text('Single line purpose for phase ' + self.name.syntax),
                           [para('Rest of purpose for phase ' + self.name.syntax)])

    @property
    def has_instructions(self) -> bool:
        return True

    @property
    def instruction_set(self) -> Optional[SectionInstructionSet]:
        return self._instruction_set


class SectionInfoTestImpl(SectionInfo):

    @property
    def cross_reference_target(self) -> CrossReferenceId:
        return CustomCrossReferenceId('section.test.impl.' + self.name.plain)

    def instruction_cross_reference_target(self, instruction_name: str) -> CrossReferenceId:
        return CustomCrossReferenceId('section-instruction.test.impl.' + self.name.plain + '.' + instruction_name)


class SectionInfoWithoutInstructionsInfoTestImpl(SectionInfoTestImpl):
    def instruction_cross_reference_target(self, instruction_name: str) -> CrossReferenceId:
        raise ValueError('The {} section do not have instructions'.format(self.name.plain))
