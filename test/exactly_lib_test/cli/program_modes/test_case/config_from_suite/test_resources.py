from exactly_lib.cli.definitions.program_modes.test_case import command_line_options
from exactly_lib.cli.main_program import TestSuiteDefinition
from exactly_lib.default import instruction_name_and_argument_splitter
from exactly_lib.section_document.element_parsers import section_element_parsers
from exactly_lib.section_document.element_parsers.optional_description_and_instruction_parser import \
    InstructionWithOptionalDescriptionParser
from exactly_lib.section_document.element_parsers.parser_for_dictionary_of_instructions import \
    InstructionParserForDictionaryOfInstructions


def cli_args_for(suite_file: str, case_file: str) -> list:
    return [command_line_options.OPTION_FOR_SUITE, suite_file, case_file]


def test_suite_definition_without_instructions() -> TestSuiteDefinition:
    return test_suite_definition_with_instructions({})


def test_suite_definition_with_instructions(configuration_section_instructions: dict) -> TestSuiteDefinition:
    parser = section_element_parsers.standard_syntax_element_parser(
        InstructionWithOptionalDescriptionParser(
            InstructionParserForDictionaryOfInstructions(
                instruction_name_and_argument_splitter.splitter,
                configuration_section_instructions))
    )

    return TestSuiteDefinition(configuration_section_instructions,
                               parser)
