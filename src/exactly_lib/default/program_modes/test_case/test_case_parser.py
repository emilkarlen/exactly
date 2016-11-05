from exactly_lib.section_document import parse
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SectionElementParserForDictionaryOfInstructions
from exactly_lib.test_case import test_case_doc, phase_identifier
from exactly_lib.test_case.instruction_setup import InstructionsSetup
from exactly_lib.util import line_source

DEFAULT_PHASE = phase_identifier.ACT


class Parser:
    def __init__(self,
                 plain_file_parser: parse.PlainDocumentParser):
        self.__plain_file_parser = plain_file_parser

    def apply(self,
              plain_test_case: line_source.LineSource) -> test_case_doc.TestCase:
        document = self.__plain_file_parser.apply(plain_test_case)
        return test_case_doc.TestCase(
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.CONFIGURATION.section_name),
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.SETUP.section_name),
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.ACT.section_name),
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.BEFORE_ASSERT.section_name),
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.ASSERT.section_name),
            document.elements_for_section_or_empty_if_phase_not_present(phase_identifier.CLEANUP.section_name),
        )


def new_parser(split_line_into_name_and_argument_function,
               act_phase_parser: parse.SectionElementParser,
               instructions_setup: InstructionsSetup) -> Parser:
    def dict_parser(instruction_set: dict) -> parse.SectionElementParser:
        return SectionElementParserForDictionaryOfInstructions(split_line_into_name_and_argument_function,
                                                               instruction_set)

    configuration = parse.SectionsConfiguration(
        (
            parse.SectionConfiguration(phase_identifier.CONFIGURATION.section_name,
                                       dict_parser(instructions_setup.config_instruction_set)),
            parse.SectionConfiguration(phase_identifier.SETUP.section_name,
                                       dict_parser(instructions_setup.setup_instruction_set)),
            parse.SectionConfiguration(phase_identifier.ACT.section_name,
                                       act_phase_parser),
            parse.SectionConfiguration(phase_identifier.BEFORE_ASSERT.section_name,
                                       dict_parser(instructions_setup.before_assert_instruction_set)),
            parse.SectionConfiguration(phase_identifier.ASSERT.section_name,
                                       dict_parser(instructions_setup.assert_instruction_set)),
            parse.SectionConfiguration(phase_identifier.CLEANUP.section_name,
                                       dict_parser(instructions_setup.cleanup_instruction_set)),
        ),
        default_section_name=DEFAULT_PHASE.section_name
    )
    return Parser(parse.new_parser_for(configuration))
