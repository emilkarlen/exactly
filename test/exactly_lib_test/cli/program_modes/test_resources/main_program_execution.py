import io
import unittest
from pathlib import Path
from typing import List

from exactly_lib.cli import main_program
from exactly_lib.cli.main_program import TestCaseDefinitionForMainProgram
from exactly_lib.cli.main_program import TestSuiteDefinition
from exactly_lib.execution.sandbox_dir_resolving import SandboxRootDirNameResolver
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.preprocessor import IDENTITY_PREPROCESSOR
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.util.file_utils.std import StdOutputFiles
from exactly_lib_test.execution.test_resources import sandbox_root_name_resolver
from exactly_lib_test.test_case.actor.test_resources.actor_impls import ActorThatRunsConstantActions
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_suite.test_resources.test_suite_definition import test_suite_definition_without_instructions


class MainProgramConfig:
    def __init__(self,
                 default_test_case_handling_setup: TestCaseHandlingSetup,
                 test_case_definition: TestCaseDefinitionForMainProgram,
                 test_suite_definition: TestSuiteDefinition,
                 sandbox_root_dir_name_resolver: SandboxRootDirNameResolver = sandbox_root_name_resolver.for_test()
                 ):
        self.default_test_case_handling_setup = default_test_case_handling_setup
        self.test_case_definition = test_case_definition
        self.test_suite_definition = test_suite_definition
        self.sandbox_root_dir_name_resolver = sandbox_root_dir_name_resolver


def main_program_config(
        tc_definition: TestCaseDefinitionForMainProgram,
        test_suite_definition: TestSuiteDefinition = test_suite_definition_without_instructions(),
        act_phase_setup: ActPhaseSetup = ActPhaseSetup(ActorThatRunsConstantActions()),
) -> MainProgramConfig:
    return MainProgramConfig(TestCaseHandlingSetup(
        act_phase_setup,
        IDENTITY_PREPROCESSOR),
        tc_definition,
        test_suite_definition,
    )


def run_main_program_and_collect_process_result(command_line_arguments: List[str],
                                                config: MainProgramConfig,
                                                ) -> SubProcessResult:
    stdout_file = io.StringIO()
    stderr_file = io.StringIO()
    std_output_files = StdOutputFiles(stdout_file=stdout_file,
                                      stderr_file=stderr_file)

    main_pgm = main_program_from_config(config)

    # ACT #

    actual_exit_code = main_pgm.execute(command_line_arguments, std_output_files)

    ret_val = SubProcessResult(actual_exit_code,
                               stdout=stdout_file.getvalue(),
                               stderr=stderr_file.getvalue())
    stdout_file.close()
    stderr_file.close()
    return ret_val


def main_program_from_config(config: MainProgramConfig) -> main_program.MainProgram:
    return main_program.MainProgram(
        config.default_test_case_handling_setup,
        config.sandbox_root_dir_name_resolver,
        config.test_case_definition,
        config.test_suite_definition,
    )


def fail_if_test_case_does_not_pass(put: unittest.TestCase,
                                    root_file_path_argument: Path,
                                    tc_definition: TestCaseDefinitionForMainProgram,
                                    ):
    # ARRANGE #

    command_line_arguments = [
        str(root_file_path_argument),
    ]

    # ACT & ASSERT #

    sub_process_result = run_main_program_and_collect_process_result(
        command_line_arguments,
        main_program_config(tc_definition)
    )

    if sub_process_result.exitcode != 0:
        put.fail('Exit code is non zero. Error message: ' + sub_process_result.stderr)


def main_program_of(test_case_definition: TestCaseDefinitionForMainProgram,
                    test_suite_definition: TestSuiteDefinition,
                    default_test_case_handling_setup: TestCaseHandlingSetup,
                    sandbox_root_dir_name_resolver: SandboxRootDirNameResolver =
                    sandbox_root_name_resolver.for_test()) -> main_program.MainProgram:
    return main_program.MainProgram(
        default_test_case_handling_setup,
        sandbox_root_dir_name_resolver,
        test_case_definition,
        test_suite_definition,
    )


def capture_output_from_main_program(command_line_arguments: List[str],
                                     main_pgm: main_program.MainProgram,
                                     ) -> SubProcessResult:
    stdout_file = io.StringIO()
    stderr_file = io.StringIO()
    std_output_files = StdOutputFiles(stdout_file=stdout_file,
                                      stderr_file=stderr_file)

    actual_exit_code = main_pgm.execute(command_line_arguments, std_output_files)

    ret_val = SubProcessResult(actual_exit_code,
                               stdout=stdout_file.getvalue(),
                               stderr=stderr_file.getvalue())
    stdout_file.close()
    stderr_file.close()
    return ret_val


def capture_output_from_main_program__in_tmp_dir(command_line_arguments: List[str],
                                                 cwd_contents: DirContents,
                                                 main_pgm: main_program.MainProgram,
                                                 ) -> SubProcessResult:
    with tmp_dir_as_cwd(cwd_contents):
        return capture_output_from_main_program(command_line_arguments, main_pgm)
