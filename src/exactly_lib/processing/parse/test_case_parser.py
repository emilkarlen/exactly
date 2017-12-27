from exactly_lib.help_texts.test_case import phase_names_plain
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup
from exactly_lib.processing.parse.instruction_section_element_parser import section_element_parser
from exactly_lib.processing.test_case_processing import TestCaseSetup
from exactly_lib.section_document import document_parser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case import test_case_doc, phase_identifier


class Parser:
    def __init__(self,
                 section_document_parser: document_parser.DocumentParser):
        self.__section_document_parser = section_document_parser

    def apply(self,
              test_case: TestCaseSetup,
              test_case_source: ParseSource) -> test_case_doc.TestCase:
        document = self.__section_document_parser.parse(test_case.file_path,
                                                        test_case.file_inclusion_relativity_root,
                                                        test_case_source)
        return test_case_doc.TestCase(
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.CONFIGURATION.section_name),
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.SETUP.section_name),
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.ACT.section_name),
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.BEFORE_ASSERT.section_name),
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.ASSERT.section_name),
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.CLEANUP.section_name),
        )


def new_parser(parsing_setup: TestCaseParsingSetup) -> Parser:
    def dict_parser(instruction_set: dict) -> document_parser.SectionElementParser:
        return section_element_parser(parsing_setup.instruction_name_extractor_function, instruction_set)

    configuration = document_parser.SectionsConfiguration(
        (
            document_parser.SectionConfiguration(
                phase_identifier.CONFIGURATION.section_name,
                dict_parser(parsing_setup.instruction_setup.config_instruction_set)),
            document_parser.SectionConfiguration(phase_identifier.SETUP.section_name,
                                                 dict_parser(
                                                     parsing_setup.instruction_setup.setup_instruction_set)),
            document_parser.SectionConfiguration(phase_identifier.ACT.section_name,
                                                 parsing_setup.act_phase_parser),
            document_parser.SectionConfiguration(
                phase_identifier.BEFORE_ASSERT.section_name,
                dict_parser(parsing_setup.instruction_setup.before_assert_instruction_set)),
            document_parser.SectionConfiguration(phase_identifier.ASSERT.section_name,
                                                 dict_parser(
                                                     parsing_setup.instruction_setup.assert_instruction_set)),
            document_parser.SectionConfiguration(phase_identifier.CLEANUP.section_name,
                                                 dict_parser(
                                                     parsing_setup.instruction_setup.cleanup_instruction_set)),
        ),
        default_section_name=phase_identifier.DEFAULT_PHASE.section_name,
        section_element_name_for_error_messages=phase_names_plain.SECTION_CONCEPT_NAME,
    )
    return Parser(document_parser.new_parser_for(configuration))
