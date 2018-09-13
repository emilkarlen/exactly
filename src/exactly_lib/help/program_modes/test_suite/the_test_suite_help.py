from typing import Dict

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.definitions.test_suite import section_names_plain
from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet
from exactly_lib.help.program_modes.test_suite.contents.section.cases import CasesSectionDocumentation
from exactly_lib.help.program_modes.test_suite.contents.section.configuration import ConfigurationSectionDocumentation
from exactly_lib.help.program_modes.test_suite.contents.section.suites import SuitesSectionDocumentation
from exactly_lib.help.program_modes.test_suite.contents.section.test_case_phase_sections import section_documentation
from exactly_lib.help.program_modes.test_suite.contents_structure.test_suite_help import TestSuiteHelp


def test_suite_help(configuration_section_instructions: Dict[str, SingleInstructionSetup]) -> TestSuiteHelp:
    """
    :param configuration_section_instructions: instruction-name -> setup
    """
    return TestSuiteHelp(
        [
            CasesSectionDocumentation(section_names_plain.SECTION_NAME__CASES),

            SuitesSectionDocumentation(section_names_plain.SECTION_NAME__SUITS),
        ],
        [
            ConfigurationSectionDocumentation(
                section_names_plain.SECTION_NAME__CONF,
                _instruction_set_help(configuration_section_instructions)
            ),
            section_documentation(
                section_names_plain.SECTION_NAME__CASE_SETUP,
                True,
            ),
            section_documentation(
                section_names_plain.SECTION_NAME__CASE_ACT,
                True,
            ),
            section_documentation(
                section_names_plain.SECTION_NAME__CASE_BEFORE_ASSERT,
                True,
            ),
            section_documentation(
                section_names_plain.SECTION_NAME__CASE_ASSERT,
                True,
            ),
            section_documentation(
                section_names_plain.SECTION_NAME__CASE_CLEANUP,
                False,
            ),
        ]
    )


def _instruction_set_help(single_instruction_setup_dic: Dict[str, SingleInstructionSetup]) -> SectionInstructionSet:
    return SectionInstructionSet(map(SingleInstructionSetup.documentation.fget, single_instruction_setup_dic.values()))
