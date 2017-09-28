from exactly_lib.cli import main_program
from exactly_lib.cli.main_program import TestCaseDefinitionForMainProgram
from exactly_lib.cli.main_program import TestSuiteDefinition
from exactly_lib.common import instruction_setup
from exactly_lib.default import instruction_name_and_argument_splitter
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.section_document import document_parser
from exactly_lib.section_document.parser_implementations import section_element_parsers
from exactly_lib.section_document.parser_implementations.optional_description_and_instruction_parser import \
    InstructionWithOptionalDescriptionParser
from exactly_lib.section_document.parser_implementations.parser_for_dictionary_of_instructions import \
    InstructionParserForDictionaryOfInstructions
from exactly_lib_test.cli.test_resources.main_program_runner_utils import \
    first_char_is_name_and_rest_is_argument__splitter, EMPTY_INSTRUCTIONS_SETUP
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.str_std_out_files import StringStdOutFiles

CONFIGURATION_SECTION_INSTRUCTIONS = instruction_setup.instruction_set_from_name_and_setup_constructor_list(
    [
    ]
)


def test_suite_definition() -> TestSuiteDefinition:
    return TestSuiteDefinition(CONFIGURATION_SECTION_INSTRUCTIONS,
                               _new_parser(),
                               _sds_root_name_prefix_for_suite)


def _new_parser() -> document_parser.SectionElementParser:
    return section_element_parsers.StandardSyntaxElementParser(
        InstructionWithOptionalDescriptionParser(
            InstructionParserForDictionaryOfInstructions(
                instruction_name_and_argument_splitter.splitter,
                CONFIGURATION_SECTION_INSTRUCTIONS)))


def _sds_root_name_prefix_for_suite():
    return 'exactly-suite-'


def execute_main_program(arguments: list,
                         the_test_case_handling_setup: TestCaseHandlingSetup,
                         instructions_setup: InstructionsSetup = EMPTY_INSTRUCTIONS_SETUP,
                         name_and_argument_splitter=first_char_is_name_and_rest_is_argument__splitter,
                         builtin_symbols: list = (),
                         test_suite_definition: TestSuiteDefinition = test_suite_definition()
                         ) -> SubProcessResult:
    str_std_out_files = StringStdOutFiles()
    program = main_program.MainProgram(str_std_out_files.stdout_files,
                                       the_test_case_handling_setup,
                                       TestCaseDefinitionForMainProgram(
                                           name_and_argument_splitter,
                                           instructions_setup,
                                           list(builtin_symbols),
                                       ),
                                       test_suite_definition)
    exit_status = program.execute(arguments)
    str_std_out_files.finish()
    return SubProcessResult(exit_status,
                            str_std_out_files.stdout_contents,
                            str_std_out_files.stderr_contents)
