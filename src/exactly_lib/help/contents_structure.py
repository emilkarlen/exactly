from exactly_lib.help.actors.actor.all_actor_docs import ALL_ACTOR_DOCS
from exactly_lib.help.actors.contents_structure import actors_help
from exactly_lib.help.concepts.all_concepts import all_concepts
from exactly_lib.help.concepts.contents_structure import concepts_help
from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet
from exactly_lib.help.program_modes.main_program.contents_structure import MainProgramHelp
from exactly_lib.help.program_modes.test_case.config import phase_help_name
from exactly_lib.help.program_modes.test_case.contents.phase import act, assert_, before_assert, configuration, \
    setup, cleanup
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp
from exactly_lib.help.program_modes.test_suite.section.cases import CasesSectionDocumentation
from exactly_lib.help.program_modes.test_suite.section.configuration import ConfigurationSectionDocumentation
from exactly_lib.help.program_modes.test_suite.section.suites import SuitesSectionDocumentation
from exactly_lib.help.suite_reporters.contents_structure import suite_reporters_help
from exactly_lib.help.suite_reporters.suite_reporter.all_suite_reporters import ALL_SUITE_REPORTERS
from exactly_lib.help.utils.entity_documentation import EntitiesHelp
from exactly_lib.help_texts.test_suite.section_names import SECTION_NAME__CONF, SECTION_NAME__SUITS, SECTION_NAME__CASES
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.test_case import phase_identifier


class ApplicationHelp(tuple):
    def __new__(cls,
                main_program_help: MainProgramHelp,
                concepts_help: EntitiesHelp,
                actors_help: EntitiesHelp,
                test_case_help: TestCaseHelp,
                test_suite_help: TestSuiteHelp,
                suite_reporters_help: EntitiesHelp):
        return tuple.__new__(cls, (main_program_help,
                                   concepts_help,
                                   test_case_help,
                                   test_suite_help,
                                   actors_help,
                                   suite_reporters_help))

    @property
    def main_program_help(self) -> MainProgramHelp:
        return self[0]

    @property
    def concepts_help(self) -> EntitiesHelp:
        return self[1]

    @property
    def test_case_help(self) -> TestCaseHelp:
        return self[2]

    @property
    def test_suite_help(self) -> TestSuiteHelp:
        return self[3]

    @property
    def actors_help(self) -> EntitiesHelp:
        return self[4]

    @property
    def suite_reporters_help(self) -> EntitiesHelp:
        return self[5]


def application_help_for_2(instructions_setup: InstructionsSetup,
                           suite_configuration_section_instructions: dict) -> ApplicationHelp:
    """
    :param instructions_setup: Test case instruction set
    :param suite_configuration_section_instructions: instruction-name -> `SingleInstructionSetup`
    """
    return ApplicationHelp(MainProgramHelp(),
                           concepts_help(all_concepts()),
                           actors_help(ALL_ACTOR_DOCS),
                           TestCaseHelp(phase_helps_for(instructions_setup)),
                           test_suite_help(suite_configuration_section_instructions),
                           suite_reporters_help(ALL_SUITE_REPORTERS))


def test_suite_help(configuration_section_instructions: dict) -> TestSuiteHelp:
    """
    :param configuration_section_instructions: instruction-name -> `SingleInstructionSetup`
    """
    return TestSuiteHelp([
        ConfigurationSectionDocumentation(SECTION_NAME__CONF,
                                          instruction_set_help(configuration_section_instructions)),
        CasesSectionDocumentation(SECTION_NAME__CASES),
        SuitesSectionDocumentation(SECTION_NAME__SUITS),
    ])


def phase_helps_for(instructions_setup: InstructionsSetup) -> iter:
    return [
        configuration.ConfigurationPhaseDocumentation(phase_help_name(phase_identifier.CONFIGURATION),
                                                      instruction_set_help(
                                                          instructions_setup.config_instruction_set)),
        setup.SetupPhaseDocumentation(phase_help_name(phase_identifier.SETUP),
                                      instruction_set_help(instructions_setup.setup_instruction_set)),
        act.ActPhaseDocumentation(phase_help_name(phase_identifier.ACT)),
        before_assert.BeforeAssertPhaseDocumentation(phase_help_name(phase_identifier.BEFORE_ASSERT),
                                                     instruction_set_help(
                                                         instructions_setup.before_assert_instruction_set)),
        assert_.AssertPhaseDocumentation(phase_help_name(phase_identifier.ASSERT),
                                         instruction_set_help(instructions_setup.assert_instruction_set)),
        cleanup.CleanupPhaseDocumentation(phase_help_name(phase_identifier.CLEANUP),
                                          instruction_set_help(instructions_setup.cleanup_instruction_set)),
    ]


def instruction_set_help(single_instruction_setup_dic: dict) -> SectionInstructionSet:
    return SectionInstructionSet(map(lambda x: x.documentation, single_instruction_setup_dic.values()))
