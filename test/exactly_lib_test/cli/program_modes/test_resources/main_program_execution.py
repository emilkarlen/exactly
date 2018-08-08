import io
from typing import List

from exactly_lib.cli import main_program
from exactly_lib.cli.main_program import TestCaseDefinitionForMainProgram, TestSuiteDefinition
from exactly_lib.execution.sandbox_dir_resolving import SandboxRootDirNameResolver
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor
from exactly_lib.util.std import StdOutputFiles
from exactly_lib_test.execution.test_resources import sandbox_root_name_resolver
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


def run_main_program_and_collect_process_result(command_line_arguments: List[str],
                                                config: MainProgramConfig,
                                                ) -> SubProcessResult:
    stdout_file = io.StringIO()
    stderr_file = io.StringIO()
    std_output_files = StdOutputFiles(stdout_file=stdout_file,
                                      stderr_file=stderr_file)

    main_pgm = main_program.MainProgram(
        std_output_files,
        config.default_test_case_handling_setup,
        config.sandbox_root_dir_name_resolver,
        config.act_phase_os_process_executor,
        config.test_case_definition,
        config.test_suite_definition,
    )

    # ACT #

    actual_exit_code = main_pgm.execute(command_line_arguments)

    ret_val = SubProcessResult(actual_exit_code,
                               stdout=stdout_file.getvalue(),
                               stderr=stderr_file.getvalue())
    stdout_file.close()
    stderr_file.close()
    return ret_val
