import io
from typing import List

from exactly_lib.cli import main_program
from exactly_lib.cli.cli_environment.program_modes.test_case import command_line_options
from exactly_lib.cli.main_program import TestCaseDefinitionForMainProgram, TestSuiteDefinition
from exactly_lib.default import instruction_name_and_argument_splitter
from exactly_lib.execution.sandbox_dir_resolving import SandboxRootDirNameResolver
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.section_document.element_parsers import section_element_parsers
from exactly_lib.section_document.element_parsers.optional_description_and_instruction_parser import \
    InstructionWithOptionalDescriptionParser
from exactly_lib.section_document.element_parsers.parser_for_dictionary_of_instructions import \
    InstructionParserForDictionaryOfInstructions
from exactly_lib.test_case import os_services
from exactly_lib.util.std import StdOutputFiles
from exactly_lib_test.execution.test_resources import sandbox_root_name_resolver
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.process import SubProcessResult


def cli_args_for(suite_file: str, case_file: str) -> list:
    return [command_line_options.OPTION_FOR_SUITE, suite_file, case_file]


def run_test_case(command_line_arguments: List[str],
                  cwd_contents: DirContents,
                  test_case_definition: TestCaseDefinitionForMainProgram,
                  test_suite_definition: TestSuiteDefinition,
                  default_test_case_handling_setup: TestCaseHandlingSetup,
                  sandbox_root_dir_name_resolver: SandboxRootDirNameResolver =
                  sandbox_root_name_resolver.for_test()
                  ) -> SubProcessResult:
    stdout_file = io.StringIO()
    stderr_file = io.StringIO()
    std_output_files = StdOutputFiles(stdout_file=stdout_file,
                                      stderr_file=stderr_file)

    main_pgm = main_program.MainProgram(
        std_output_files,
        default_test_case_handling_setup,
        sandbox_root_dir_name_resolver,
        os_services.DEFAULT_ACT_PHASE_OS_PROCESS_EXECUTOR,
        test_case_definition,
        test_suite_definition,
    )
    with tmp_dir_as_cwd(cwd_contents):
        # ACT #
        actual_exit_code = main_pgm.execute(command_line_arguments)

    ret_val = SubProcessResult(actual_exit_code,
                               stdout=stdout_file.getvalue(),
                               stderr=stderr_file.getvalue())
    stdout_file.close()
    stderr_file.close()
    return ret_val


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
