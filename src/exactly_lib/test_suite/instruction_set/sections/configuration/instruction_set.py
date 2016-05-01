from exactly_lib.common.instruction_setup import instruction_set_from_name_and_setup_constructor_list
from exactly_lib.default.program_modes.test_case import instruction_name_and_argument_splitter
from exactly_lib.section_document import parse
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SectionElementParserForDictionaryOfInstructions
from exactly_lib.test_suite.instruction_set.sections.configuration import preprocessor


CONFIGURATION_INSTRUCTIONS = instruction_set_from_name_and_setup_constructor_list(
    [
        ('preprocessor', preprocessor.setup),
    ]
)


def new_parser() -> parse.SectionElementParser:
    return SectionElementParserForDictionaryOfInstructions(
        instruction_name_and_argument_splitter.splitter,
        CONFIGURATION_INSTRUCTIONS,
    )
