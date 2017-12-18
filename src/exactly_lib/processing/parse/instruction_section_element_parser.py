from typing import Dict

from exactly_lib.section_document import document_parser
from exactly_lib.section_document.parser_implementations.optional_description_and_instruction_parser import \
    InstructionWithOptionalDescriptionParser
from exactly_lib.section_document.parser_implementations.parser_for_dictionary_of_instructions import \
    InstructionParserForDictionaryOfInstructions, InstructionNameExtractor
from exactly_lib.section_document.parser_implementations.section_element_parsers import StandardSyntaxElementParser, \
    InstructionParser


def instruction_parser(instruction_name_extractor_function: InstructionNameExtractor,
                       instruction_set: Dict[str, InstructionParser]) -> InstructionParser:
    return InstructionParserForDictionaryOfInstructions(instruction_name_extractor_function,
                                                        instruction_set)


def section_element_parser_of(the_instruction_parser: InstructionParser) -> document_parser.SectionElementParser:
    return StandardSyntaxElementParser(
        InstructionWithOptionalDescriptionParser(the_instruction_parser))


def section_element_parser(instruction_name_extractor_function: InstructionNameExtractor,
                           instruction_set: Dict[str, InstructionParser]) -> document_parser.SectionElementParser:
    return section_element_parser_of(
        instruction_parser(instruction_name_extractor_function,
                           instruction_set))
