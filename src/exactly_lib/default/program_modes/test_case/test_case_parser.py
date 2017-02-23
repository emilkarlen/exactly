from exactly_lib.processing.instruction_setup import InstructionsSetup
# TODO [instr-desc] Rename when new parser structures are fully integrated
from exactly_lib.section_document import new_parser_classes as parse2
from exactly_lib.section_document.new_parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.new_section_element_parser import StandardSyntaxElementParser
from exactly_lib.section_document.parser_implementations.optional_description_and_instruction_parser import \
    InstructionWithOptionalDescriptionParser
from exactly_lib.section_document.parser_implementations.parser_for_dictionary_of_instructions import \
    InstructionParserForDictionaryOfInstructions
from exactly_lib.test_case import test_case_doc, phase_identifier


class Parser:
    def __init__(self,
                 plain_file_parser: parse2.DocumentParser):
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


def new_parser(instruction_name_extractor_function,
               act_phase_parser: parse2.SectionElementParser,
               instructions_setup: InstructionsSetup) -> Parser:
    def dict_parser(instruction_set: dict) -> parse2.SectionElementParser:
        return StandardSyntaxElementParser(
            InstructionWithOptionalDescriptionParser(
                InstructionParserForDictionaryOfInstructions(instruction_name_extractor_function,
                                                             instruction_set)))

    configuration = parse2.SectionsConfiguration(
        (
            parse2.SectionConfiguration(
                phase_identifier.CONFIGURATION.section_name,
                dict_parser(instructions_setup.config_instruction_set)),
            parse2.SectionConfiguration(phase_identifier.SETUP.section_name,
                                        dict_parser(
                                            instructions_setup.setup_instruction_set)),
            parse2.SectionConfiguration(phase_identifier.ACT.section_name,
                                        act_phase_parser),
            parse2.SectionConfiguration(
                phase_identifier.BEFORE_ASSERT.section_name,
                dict_parser(instructions_setup.before_assert_instruction_set)),
            parse2.SectionConfiguration(phase_identifier.ASSERT.section_name,
                                        dict_parser(
                                            instructions_setup.assert_instruction_set)),
            parse2.SectionConfiguration(phase_identifier.CLEANUP.section_name,
                                        dict_parser(
                                            instructions_setup.cleanup_instruction_set)),
        ),
        default_section_name=phase_identifier.DEFAULT_PHASE.section_name,
        section_element_name_for_error_messages=phase_identifier.SECTION_CONCEPT_NAME,
    )
    return Parser(parse2.new_parser_for(configuration))
