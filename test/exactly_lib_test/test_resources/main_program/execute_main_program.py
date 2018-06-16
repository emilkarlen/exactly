from typing import List, Sequence

from exactly_lib.cli import main_program
from exactly_lib.cli.main_program import TestCaseDefinitionForMainProgram, BuiltinSymbol
from exactly_lib.cli.main_program import TestSuiteDefinition
from exactly_lib.common import instruction_setup
from exactly_lib.default import instruction_name_and_argument_splitter
from exactly_lib.processing.instruction_setup import InstructionsSetup, TestCaseParsingSetup
from exactly_lib.processing.parse.act_phase_source_parser import ActPhaseParser
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.section_document import document_parser
from exactly_lib.section_document.element_parsers import section_element_parsers
from exactly_lib.section_document.element_parsers.optional_description_and_instruction_parser import \
    InstructionWithOptionalDescriptionParser
from exactly_lib.section_document.element_parsers.parser_for_dictionary_of_instructions import \
    InstructionParserForDictionaryOfInstructions
from exactly_lib.test_case import os_services
from exactly_lib_test.execution.test_resources import sandbox_root_name_resolver
from exactly_lib_test.test_resources.files.str_std_out_files import StringStdOutFiles
from exactly_lib_test.test_resources.main_program.main_program_runner_utils import \
    first_char_is_name_and_rest_is_argument__splitter, EMPTY_INSTRUCTIONS_SETUP
from exactly_lib_test.test_resources.process import SubProcessResult

CONFIGURATION_SECTION_INSTRUCTIONS = instruction_setup.instruction_set_from_name_and_setup_constructor_list(
    [
    ]
)


def test_suite_definition() -> TestSuiteDefinition:
    return TestSuiteDefinition(CONFIGURATION_SECTION_INSTRUCTIONS,
                               _new_parser(),
                               sandbox_root_name_resolver.prefix_for_suite)


def _new_parser() -> document_parser.SectionElementParser:
    return section_element_parsers.standard_syntax_element_parser(
        InstructionWithOptionalDescriptionParser(
            InstructionParserForDictionaryOfInstructions(
                instruction_name_and_argument_splitter.splitter,
                CONFIGURATION_SECTION_INSTRUCTIONS)))


def execute_main_program(arguments: List[str],
                         the_test_case_handling_setup: TestCaseHandlingSetup,
                         instructions_setup: InstructionsSetup = EMPTY_INSTRUCTIONS_SETUP,
                         name_and_argument_splitter=first_char_is_name_and_rest_is_argument__splitter,
                         builtin_symbols: Sequence[BuiltinSymbol] = (),
                         test_suite_definition: TestSuiteDefinition = test_suite_definition()
                         ) -> SubProcessResult:
    str_std_out_files = StringStdOutFiles()
    program = main_program.MainProgram(str_std_out_files.stdout_files,
                                       the_test_case_handling_setup,
                                       sandbox_root_name_resolver.for_test(),
                                       os_services.DEFAULT_ACT_PHASE_OS_PROCESS_EXECUTOR,
                                       TestCaseDefinitionForMainProgram(
                                           TestCaseParsingSetup(name_and_argument_splitter,
                                                                instructions_setup,
                                                                ActPhaseParser()),
                                           list(builtin_symbols),
                                       ),
                                       test_suite_definition)
    exit_status = program.execute(arguments)
    str_std_out_files.finish()
    return SubProcessResult(exit_status,
                            str_std_out_files.stdout_contents,
                            str_std_out_files.stderr_contents)
