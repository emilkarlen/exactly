from typing import Dict

from exactly_lib.help_texts.test_case.instructions import instruction_names
from exactly_lib.processing.parse.file_inclusion_directive_parser import FileInclusionDirectiveParser
from exactly_lib.section_document import document_parser
from exactly_lib.section_document.element_parsers.optional_description_and_instruction_parser import \
    InstructionWithOptionalDescriptionParser
from exactly_lib.section_document.element_parsers.parser_for_dictionary_of_instructions import \
    InstructionParserForDictionaryOfInstructions, InstructionNameExtractor
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser, \
    ParserFromSequenceOfParsers, StandardSyntaxCommentAndEmptyLineParser


def instruction_parser(instruction_name_extractor_function: InstructionNameExtractor,
                       instruction_set: Dict[str, InstructionParser]) -> InstructionParser:
    return InstructionParserForDictionaryOfInstructions(instruction_name_extractor_function,
                                                        instruction_set)


def section_element_parser_of(the_instruction_parser: InstructionParser) -> document_parser.SectionElementParser:
    return ParserFromSequenceOfParsers([
        StandardSyntaxCommentAndEmptyLineParser(),
        FileInclusionDirectiveParser(instruction_names.FILE_INCLUSION_DIRECTIVE_NAME),
        InstructionWithOptionalDescriptionParser(the_instruction_parser)
    ])


def section_element_parser(instruction_name_extractor_function: InstructionNameExtractor,
                           instruction_set: Dict[str, InstructionParser]) -> document_parser.SectionElementParser:
    return section_element_parser_of(
        instruction_parser(instruction_name_extractor_function,
                           instruction_set))
