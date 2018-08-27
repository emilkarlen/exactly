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
from exactly_lib.test_case import os_services
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor
from exactly_lib.util.std import StdOutputFiles
from exactly_lib_test.cli.program_modes.test_case.config_from_suite.test_resources import \
    test_suite_definition_without_instructions
from exactly_lib_test.execution.test_resources import sandbox_root_name_resolver
from exactly_lib_test.test_case.act_phase_handling.test_resources.act_source_and_executor_constructors import \
    ActSourceAndExecutorConstructorThatRunsConstantActions
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.process import SubProcessResult


class MainProgramConfig:
    def __init__(self,
                 default_test_case_handling_setup: TestCaseHandlingSetup,
                 act_phase_os_process_executor: ActPhaseOsProcessExecutor,
                 test_case_definition: TestCaseDefinitionForMainProgram,
                 test_suite_definition: TestSuiteDefinition,
                 sandbox_root_dir_name_resolver: SandboxRootDirNameResolver = sandbox_root_name_resolver.for_test()
                 ):
        self.default_test_case_handling_setup = default_test_case_handling_setup
        self.act_phase_os_process_executor = act_phase_os_process_executor
        self.test_case_definition = test_case_definition
        self.test_suite_definition = test_suite_definition
        self.sandbox_root_dir_name_resolver = sandbox_root_dir_name_resolver


def main_program_config(tc_definition: TestCaseDefinitionForMainProgram) -> MainProgramConfig:
    return MainProgramConfig(TestCaseHandlingSetup(
        ActPhaseSetup(ActSourceAndExecutorConstructorThatRunsConstantActions()),
        IDENTITY_PREPROCESSOR),
        os_services.DEFAULT_ACT_PHASE_OS_PROCESS_EXECUTOR,
        tc_definition,
        test_suite_definition_without_instructions(),
    )


def run_main_program_and_collect_process_result(command_line_arguments: List[str],
                                                config: MainProgramConfig,
                                                ) -> SubProcessResult:
    stdout_file = io.StringIO()
    stderr_file = io.StringIO()
    std_output_files = StdOutputFiles(stdout_file=stdout_file,
                                      stderr_file=stderr_file)

    main_pgm = main_program.MainProgram(
        config.default_test_case_handling_setup,
        config.sandbox_root_dir_name_resolver,
        config.act_phase_os_process_executor,
        config.test_case_definition,
        config.test_suite_definition,
    )

    # ACT #

    actual_exit_code = main_pgm.execute(command_line_arguments, std_output_files)

    ret_val = SubProcessResult(actual_exit_code,
                               stdout=stdout_file.getvalue(),
                               stderr=stderr_file.getvalue())
    stdout_file.close()
    stderr_file.close()
    return ret_val


def fail_if_test_case_does_not_pass(put: unittest.TestCase,
                                    root_file_path_argument: Path,
                                    tc_definition: TestCaseDefinitionForMainProgram,
                                    ):
    # SETUP #

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
        os_services.DEFAULT_ACT_PHASE_OS_PROCESS_EXECUTOR,
        test_case_definition,
        test_suite_definition,
    )


def run_test_case(command_line_arguments: List[str],
                  cwd_contents: DirContents,
                  main_pgm: main_program.MainProgram,
                  ) -> SubProcessResult:
    stdout_file = io.StringIO()
    stderr_file = io.StringIO()
    std_output_files = StdOutputFiles(stdout_file=stdout_file,
                                      stderr_file=stderr_file)

    with tmp_dir_as_cwd(cwd_contents):
        # ACT #
        actual_exit_code = main_pgm.execute(command_line_arguments, std_output_files)

    ret_val = SubProcessResult(actual_exit_code,
                               stdout=stdout_file.getvalue(),
                               stderr=stderr_file.getvalue())
    stdout_file.close()
    stderr_file.close()
    return ret_val
