from typing import List, Sequence

from exactly_lib.cli import main_program
from exactly_lib.cli.main_program import TestCaseDefinitionForMainProgram, BuiltinSymbol
from exactly_lib.cli.main_program import TestSuiteDefinition
from exactly_lib.common import instruction_setup, instruction_name_and_argument_splitter
from exactly_lib.processing.instruction_setup import InstructionsSetup, TestCaseParsingSetup
from exactly_lib.processing.parse.act_phase_source_parser import ActPhaseParser
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.section_document.element_parsers import section_element_parsers
from exactly_lib.section_document.element_parsers.optional_description_and_instruction_parser import \
    InstructionWithOptionalDescriptionParser
from exactly_lib.section_document.element_parsers.parser_for_dictionary_of_instructions import \
    InstructionParserForDictionaryOfInstructions
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.util.file_utils.std import StdOutputFiles
from exactly_lib_test.execution.test_resources import sandbox_root_name_resolver
from exactly_lib_test.test_resources.files.capture_out_files import capture_stdout_err
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


def _new_parser() -> SectionElementParser:
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
                         test_suite_def: TestSuiteDefinition = test_suite_definition()
                         ) -> SubProcessResult:
    program = main_program.MainProgram(the_test_case_handling_setup,
                                       sandbox_root_name_resolver.for_test(),
                                       TestCaseDefinitionForMainProgram(
                                           TestCaseParsingSetup(name_and_argument_splitter,
                                                                instructions_setup,
                                                                ActPhaseParser()),
                                           list(builtin_symbols),
                                       ),
                                       test_suite_def)

    def action_with_stdout_files(stdout_files: StdOutputFiles) -> int:
        return program.execute(arguments, stdout_files)

    std_out_files, exit_code = capture_stdout_err(action_with_stdout_files)
    return SubProcessResult(exit_code,
                            std_out_files.out,
                            std_out_files.err)
