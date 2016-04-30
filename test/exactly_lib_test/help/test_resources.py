from exactly_lib.help.contents_structure import ApplicationHelp
from exactly_lib.help.cross_reference_id import CrossReferenceId
from exactly_lib.help.program_modes.main_program.contents_structure import MainProgramHelp
from exactly_lib.help.program_modes.test_case.contents_structure import TestCasePhaseInstructionSet, \
    TestCasePhaseDocumentation, ConceptsHelp, TestCaseHelp
from exactly_lib.help.program_modes.test_case.instruction_documentation import InstructionDocumentation
from exactly_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp
from exactly_lib.help.utils.cross_reference import CrossReferenceTextConstructor
from exactly_lib.help.utils.description import Description
from exactly_lib.help.utils.render import RenderingEnvironment
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.core import Text
from exactly_lib.util.textformat.structure.structures import para, text
from exactly_lib_test.test_resources.instruction_description import InstructionDocumentationWithConstantValues


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
                         instruction_names: list) -> TestCasePhaseDocumentation:
    instruction_set = test_case_phase_instruction_set(phase_name, instruction_names)
    return TestCasePhaseHelpForPhaseWithInstructionsTestImpl(phase_name,
                                                             instruction_set)


def test_case_phase_instruction_set(phase_name: str,
                                    instruction_names: list) -> TestCasePhaseInstructionSet:
    instruction_descriptions = map(lambda name: instr_descr(phase_name, name),
                                   instruction_names)
    return TestCasePhaseInstructionSet(instruction_descriptions)


def application_help_for(test_case_phase_helps: list,
                         suite_sections=(),
                         concepts=()) -> ApplicationHelp:
    return ApplicationHelp(MainProgramHelp(),
                           ConceptsHelp(concepts),
                           TestCaseHelp(test_case_phase_helps),
                           TestSuiteHelp(suite_sections))


class TestCasePhaseHelpForPhaseWithInstructionsTestImpl(TestCasePhaseDocumentation):
    def __init__(self,
                 name: str,
                 instruction_set: TestCasePhaseInstructionSet):
        super().__init__(name)
        self._instruction_set = instruction_set

    def purpose(self) -> Description:
        return Description(text('Single line purpose for phase ' + self.name.syntax),
                           [para('Rest of purpose for phase ' + self.name.syntax)])

    def render(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return doc.SectionContents([para('Rendition of phase {0:emphasis}'.format(self.name))],
                                   [])

    @property
    def is_phase_with_instructions(self) -> bool:
        return True

    @property
    def instruction_set(self) -> TestCasePhaseInstructionSet:
        return self._instruction_set


class CrossReferenceTextConstructorTestImpl(CrossReferenceTextConstructor):
    def apply(self, x: CrossReferenceId) -> Text:
        return 'Reference to ' + str(x)
