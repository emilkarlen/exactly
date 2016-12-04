from exactly_lib.common.instruction_documentation import InstructionDocumentation
from exactly_lib.help.actors.contents_structure import actors_help
from exactly_lib.help.concepts.contents_structure import concepts_help
from exactly_lib.help.contents_structure import ApplicationHelp
from exactly_lib.help.cross_reference_id import CrossReferenceId
from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet, \
    SectionDocumentation
from exactly_lib.help.program_modes.main_program.contents_structure import MainProgramHelp
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp
from exactly_lib.help.suite_reporters.contents_structure import suite_reporters_help
from exactly_lib.help.utils.cross_reference import CrossReferenceTextConstructor
from exactly_lib.help.utils.render import RenderingEnvironment
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.core import Text
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
                          instruction_names: list) -> SectionDocumentation:
    instruction_set = section_instruction_set(phase_name, instruction_names)
    return SectionDocumentationForSectionWithInstructionsTestImpl(phase_name,
                                                                  instruction_set)


def section_instruction_set(section_name: str,
                            instruction_names: list) -> SectionInstructionSet:
    instruction_descriptions = map(lambda name: instr_descr(section_name, name),
                                   instruction_names)
    return SectionInstructionSet(instruction_descriptions)


def application_help_for(test_case_phase_helps: list,
                         suite_sections=(),
                         concepts=(),
                         actors=(),
                         suite_reporters=()) -> ApplicationHelp:
    return ApplicationHelp(MainProgramHelp(),
                           concepts_help(concepts),
                           actors_help(actors),
                           TestCaseHelp(test_case_phase_helps),
                           TestSuiteHelp(suite_sections),
                           suite_reporters_help(suite_reporters))


def application_help_for_suite_sections(suite_sections: list) -> ApplicationHelp:
    return ApplicationHelp(MainProgramHelp(),
                           concepts_help([]),
                           actors_help([]),
                           TestCaseHelp([]),
                           TestSuiteHelp(suite_sections),
                           suite_reporters_help([]))


class SectionDocumentationForSectionWithoutInstructionsTestImpl(SectionDocumentation):
    def __init__(self,
                 name: str):
        super().__init__(name)

    def purpose(self) -> Description:
        return Description(text('Single line purpose for phase ' + self.name.syntax),
                           [para('Rest of purpose for phase ' + self.name.syntax)])

    def render(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return doc.SectionContents([para('Rendition of section {0:emphasis}'.format(self.name))],
                                   [])

    @property
    def has_instructions(self) -> bool:
        return False

    @property
    def instruction_set(self) -> SectionInstructionSet:
        raise NotImplementedError('This section does not have instructions.')


class SectionDocumentationForSectionWithInstructionsTestImpl(SectionDocumentation):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        super().__init__(name)
        self._instruction_set = instruction_set

    def purpose(self) -> Description:
        return Description(text('Single line purpose for phase ' + self.name.syntax),
                           [para('Rest of purpose for phase ' + self.name.syntax)])

    def render(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return doc.SectionContents([para('Rendition of section {0:emphasis}'.format(self.name))],
                                   [])

    @property
    def has_instructions(self) -> bool:
        return True

    @property
    def instruction_set(self) -> SectionInstructionSet:
        return self._instruction_set


class CrossReferenceTextConstructorTestImpl(CrossReferenceTextConstructor):
    def apply(self, x: CrossReferenceId) -> Text:
        return 'Reference to ' + str(x)
