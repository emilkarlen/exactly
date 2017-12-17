from typing import Callable

from exactly_lib.help_texts.test_case import phase_names_plain
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.processing.parse.instruction_section_element_parser import section_element_parser
from exactly_lib.section_document import document_parser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case import test_case_doc, phase_identifier


class Parser:
    def __init__(self,
                 plain_file_parser: document_parser.DocumentParser):
        self.__plain_file_parser = plain_file_parser

    def apply(self,
              plain_test_case: ParseSource) -> test_case_doc.TestCase:
        document = self.__plain_file_parser.parse(plain_test_case)
        return test_case_doc.TestCase(
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.CONFIGURATION.section_name),
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.SETUP.section_name),
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.ACT.section_name),
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.BEFORE_ASSERT.section_name),
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.ASSERT.section_name),
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.CLEANUP.section_name),
        )


def new_parser(instruction_name_extractor_function: Callable[[str], str],
               act_phase_parser: document_parser.SectionElementParser,
               instructions_setup: InstructionsSetup) -> Parser:
    def dict_parser(instruction_set: dict) -> document_parser.SectionElementParser:
        return section_element_parser(instruction_name_extractor_function, instruction_set)

    configuration = document_parser.SectionsConfiguration(
        (
            document_parser.SectionConfiguration(
                phase_identifier.CONFIGURATION.section_name,
                dict_parser(instructions_setup.config_instruction_set)),
            document_parser.SectionConfiguration(phase_identifier.SETUP.section_name,
                                                 dict_parser(
                                                     instructions_setup.setup_instruction_set)),
            document_parser.SectionConfiguration(phase_identifier.ACT.section_name,
                                                 act_phase_parser),
            document_parser.SectionConfiguration(
                phase_identifier.BEFORE_ASSERT.section_name,
                dict_parser(instructions_setup.before_assert_instruction_set)),
            document_parser.SectionConfiguration(phase_identifier.ASSERT.section_name,
                                                 dict_parser(
                                                     instructions_setup.assert_instruction_set)),
            document_parser.SectionConfiguration(phase_identifier.CLEANUP.section_name,
                                                 dict_parser(
                                                     instructions_setup.cleanup_instruction_set)),
        ),
        default_section_name=phase_identifier.DEFAULT_PHASE.section_name,
        section_element_name_for_error_messages=phase_names_plain.SECTION_CONCEPT_NAME,
    )
    return Parser(document_parser.new_parser_for(configuration))
