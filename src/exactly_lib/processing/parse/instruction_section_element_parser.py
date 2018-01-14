from typing import Dict

from exactly_lib.section_document import document_parser
from exactly_lib.section_document.element_parsers.optional_description_and_instruction_parser import \
    InstructionWithOptionalDescriptionParser
from exactly_lib.section_document.element_parsers.parser_for_dictionary_of_instructions import \
    InstructionParserForDictionaryOfInstructions, InstructionNameExtractor
from exactly_lib.section_document.element_parsers.section_element_parsers import standard_syntax_element_parser, \
    InstructionParser


def instruction_parser(instruction_name_extractor_function: InstructionNameExtractor,
                       instruction_set: Dict[str, InstructionParser]) -> InstructionParser:
    return InstructionParserForDictionaryOfInstructions(instruction_name_extractor_function,
                                                        instruction_set)


def section_element_parser_of(the_instruction_parser: InstructionParser) -> document_parser.SectionElementParser:
    return standard_syntax_element_parser(
        InstructionWithOptionalDescriptionParser(the_instruction_parser))


def section_element_parser(instruction_name_extractor_function: InstructionNameExtractor,
                           instruction_set: Dict[str, InstructionParser]) -> document_parser.SectionElementParser:
    return section_element_parser_of(
        instruction_parser(instruction_name_extractor_function,
                           instruction_set))
