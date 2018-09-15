import datetime

from exactly_lib import program_info
from exactly_lib.cli.main_program import TestSuiteDefinition
from exactly_lib.common import instruction_setup, instruction_name_and_argument_splitter
from exactly_lib.definitions.test_suite import instruction_names
from exactly_lib.section_document.element_parsers import section_element_parsers
from exactly_lib.section_document.element_parsers.optional_description_and_instruction_parser import \
    InstructionWithOptionalDescriptionParser
from exactly_lib.section_document.element_parsers.parser_for_dictionary_of_instructions import \
    InstructionParserForDictionaryOfInstructions
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.test_suite.instruction_set.sections.configuration import preprocessor

CONFIGURATION_SECTION_INSTRUCTIONS = instruction_setup.instruction_set_from_name_and_setup_constructor_list(
    [
        (instruction_names.INSTRUCTION_NAME__PREPROCESSOR, preprocessor.setup),
    ]
)


def new_parser() -> SectionElementParser:
    return section_element_parsers.standard_syntax_element_parser(
        InstructionWithOptionalDescriptionParser(
            InstructionParserForDictionaryOfInstructions(
                instruction_name_and_argument_splitter.splitter,
                CONFIGURATION_SECTION_INSTRUCTIONS)))


def test_suite_definition() -> TestSuiteDefinition:
    return TestSuiteDefinition(CONFIGURATION_SECTION_INSTRUCTIONS,
                               new_parser(),
                               _sds_root_name_prefix_for_suite)


def _sds_root_name_prefix_for_suite():
    today = datetime.datetime.today()
    datetime_suffix = today.strftime('%Y-%m-%d-%H-%M-%S')
    sandbox_directory_root_name_prefix = program_info.PROGRAM_NAME + '-suite-' + datetime_suffix + '-'
    return sandbox_directory_root_name_prefix
