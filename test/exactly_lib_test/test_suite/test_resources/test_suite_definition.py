from typing import Dict

from exactly_lib.cli.main_program import TestSuiteDefinition
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.default import instruction_name_and_argument_splitter
from exactly_lib.section_document.element_parsers import section_element_parsers
from exactly_lib.section_document.element_parsers.optional_description_and_instruction_parser import \
    InstructionWithOptionalDescriptionParser
from exactly_lib.section_document.element_parsers.parser_for_dictionary_of_instructions import \
    InstructionParserForDictionaryOfInstructions
from exactly_lib.section_document.section_element_parsing import SectionElementParser


def test_suite_definition_without_instructions() -> TestSuiteDefinition:
    return test_suite_definition_with_instructions({})


def test_suite_definition_with_instructions(configuration_section_instructions: Dict[str, SingleInstructionSetup]
                                            ) -> TestSuiteDefinition:
    parser = configuration_section_parser(configuration_section_instructions)

    return TestSuiteDefinition(configuration_section_instructions,
                               parser)


def configuration_section_parser(configuration_section_instructions: Dict[str, SingleInstructionSetup]
                                 ) -> SectionElementParser:
    return section_element_parsers.standard_syntax_element_parser(
        InstructionWithOptionalDescriptionParser(
            InstructionParserForDictionaryOfInstructions(
                instruction_name_and_argument_splitter.splitter,
                configuration_section_instructions))
    )
