from exactly_lib.common.instruction_setup import instruction_set_from_name_and_setup_constructor_list
from exactly_lib.default import instruction_name_and_argument_splitter
from exactly_lib.section_document import document_parser
from exactly_lib.section_document.parser_implementations.optional_description_and_instruction_parser import \
    InstructionWithOptionalDescriptionParser
from exactly_lib.section_document.parser_implementations.parser_for_dictionary_of_instructions import \
    InstructionParserForDictionaryOfInstructions
from exactly_lib.section_document.parser_implementations.section_element_parsers import StandardSyntaxElementParser
from exactly_lib.test_suite.instruction_set.sections.configuration import preprocessor, actor

INSTRUCTION_NAME__PREPROCESSOR = 'preprocessor'

INSTRUCTION_NAME__ACTOR = 'actor'

CONFIGURATION_INSTRUCTIONS = instruction_set_from_name_and_setup_constructor_list(
    [
        (INSTRUCTION_NAME__PREPROCESSOR, preprocessor.setup),
        (INSTRUCTION_NAME__ACTOR, actor.setup),
    ]
)


def new_parser() -> document_parser.SectionElementParser:
    return StandardSyntaxElementParser(
        InstructionWithOptionalDescriptionParser(
            InstructionParserForDictionaryOfInstructions(
                instruction_name_and_argument_splitter.splitter,
                CONFIGURATION_INSTRUCTIONS)))
