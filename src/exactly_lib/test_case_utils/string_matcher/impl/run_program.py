import pathlib

from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.test_case_utils.matcher.impls.run_program import sdv as run_pgm_sdv
from exactly_lib.test_case_utils.matcher.impls.run_program.runner import Runner
from exactly_lib.test_case_utils.program_execution.command_executor import CommandExecutor
from exactly_lib.test_case_utils.program_execution.exe_wo_transformation import ExecutionResultAndStderr
from exactly_lib.test_case_utils.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.type_system.logic.program.program import Program
from exactly_lib.type_system.logic.string_matcher import StringMatcherSdv
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.util.process_execution import file_ctx_managers
from exactly_lib.util.process_execution.exe_store_and_read_stderr import ExecutorThatReadsStderrOnNonZeroExitCode, \
    Result
from exactly_lib.util.process_execution.process_executor import ProcessExecutor


def sdv(program: ProgramSdv) -> StringMatcherSdv:
    return run_pgm_sdv.sdv(_StringMatcherRunner, program)


class _StringMatcherRunner(Runner[StringModel]):
    def run(self, program_for_model: Program, model: StringModel) -> ExecutionResultAndStderr:
        command_executor = self._command_executor(model)
        app_env = self._application_environment
        result = command_executor.execute(app_env.process_execution_settings,
                                          program_for_model.command,
                                          program_for_model.structure())
        return ExecutionResultAndStderr(
            result.exit_code,
            result.stderr,
            pathlib.Path('unused'),
            program_for_model.structure(),
        )

    def _command_executor(self, model: StringModel) -> CommandExecutor[Result]:
        app_env = self._application_environment
        path_of_file_with_model = model.as_file
        return CommandExecutor(
            app_env.os_services,
            ExecutorThatReadsStderrOnNonZeroExitCode(
                ProcessExecutor(),
                app_env.tmp_files_space,
                file_ctx_managers.open_file(path_of_file_with_model, 'r'),
            )
        )

    def program_for_model(self, matcher_argument_program: Program, model: StringModel) -> Program:
        return Program(
            matcher_argument_program.command,
            matcher_argument_program.stdin,
            IdentityStringTransformer(),
        )
