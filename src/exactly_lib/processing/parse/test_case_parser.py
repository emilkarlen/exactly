from typing import Dict, Callable

from exactly_lib.definitions.test_case import phase_names_plain
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup, InstructionsSetup
from exactly_lib.processing.parse.instruction_section_element_parser import section_element_parser
from exactly_lib.processing.test_case_processing import TestCaseFileReference
from exactly_lib.section_document import document_parsers
from exactly_lib.section_document import section_parsing
from exactly_lib.section_document.document_parser import DocumentParser
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.test_case import test_case_doc, phase_identifier


class Parser:
    def __init__(self,
                 section_document_parser: DocumentParser):
        self.__section_document_parser = section_document_parser

    def apply(self,
              test_case: TestCaseFileReference,
              test_case_source: ParseSource) -> test_case_doc.TestCase:
        document = self.__section_document_parser.parse_source(test_case.file_path,
                                                               test_case_source)
        return test_case_doc.TestCase(
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.CONFIGURATION.section_name),
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.SETUP.section_name),
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.ACT.section_name),
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.BEFORE_ASSERT.section_name),
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.ASSERT.section_name),
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.CLEANUP.section_name),
        )


class SectionParserConstructorForParsingSetup:
    def __init__(self, parsing_setup: TestCaseParsingSetup):
        self.parsing_setup = parsing_setup

    def of(self,
           phase_instructions: Callable[[InstructionsSetup], Dict[str, InstructionParser]]) -> SectionElementParser:
        return section_element_parser(self.parsing_setup.instruction_name_extractor_function,
                                      phase_instructions(self.parsing_setup.instruction_setup))


def new_parser(parsing_setup: TestCaseParsingSetup) -> Parser:
    parser_con = SectionParserConstructorForParsingSetup(parsing_setup)

    configuration = section_parsing.SectionsConfiguration(
        (
            section_parsing.SectionConfiguration(phase_identifier.CONFIGURATION.section_name,
                                                 parser_con.of(InstructionsSetup.config_instruction_set.fget)),

            section_parsing.SectionConfiguration(phase_identifier.SETUP.section_name,
                                                 parser_con.of(InstructionsSetup.setup_instruction_set.fget)),

            section_parsing.SectionConfiguration(phase_identifier.ACT.section_name,
                                                 parsing_setup.act_phase_parser),

            section_parsing.SectionConfiguration(phase_identifier.BEFORE_ASSERT.section_name,
                                                 parser_con.of(InstructionsSetup.before_assert_instruction_set.fget)),

            section_parsing.SectionConfiguration(phase_identifier.ASSERT.section_name,
                                                 parser_con.of(InstructionsSetup.assert_instruction_set.fget)),

            section_parsing.SectionConfiguration(phase_identifier.CLEANUP.section_name,
                                                 parser_con.of(InstructionsSetup.cleanup_instruction_set.fget)),
        ),
        default_section_name=phase_identifier.DEFAULT_PHASE.section_name,
        section_element_name_for_error_messages=phase_names_plain.SECTION_CONCEPT_NAME,
    )
    return Parser(document_parsers.new_parser_for(configuration))
