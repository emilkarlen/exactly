from typing import Dict

from exactly_lib.definitions.entity import directives
from exactly_lib.processing.parse.file_inclusion_directive_parser import FileInclusionDirectiveParser
from exactly_lib.section_document.element_parsers.optional_description_and_instruction_parser import \
    InstructionWithOptionalDescriptionParser
from exactly_lib.section_document.element_parsers.parser_for_dictionary_of_instructions import \
    InstructionParserForDictionaryOfInstructions, InstructionNameExtractor
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser, \
    ParserFromSequenceOfParsers, StandardSyntaxCommentAndEmptyLineParser
from exactly_lib.section_document.section_element_parsing import SectionElementParser


def instruction_parser(instruction_name_extractor_function: InstructionNameExtractor,
                       instruction_set: Dict[str, InstructionParser]) -> InstructionParser:
    return InstructionParserForDictionaryOfInstructions(instruction_name_extractor_function,
                                                        instruction_set)


def section_element_parser_of(
        the_instruction_parser: InstructionParser) -> SectionElementParser:
    return ParserFromSequenceOfParsers([
        StandardSyntaxCommentAndEmptyLineParser(),
        FileInclusionDirectiveParser(directives.INCLUDING_DIRECTIVE_INFO.singular_name),
        InstructionWithOptionalDescriptionParser(the_instruction_parser)
    ])


def section_element_parser(instruction_name_extractor_function: InstructionNameExtractor,
                           instruction_set: Dict[
                               str, InstructionParser]) -> SectionElementParser:
    return section_element_parser_of(
        instruction_parser(instruction_name_extractor_function,
                           instruction_set))
