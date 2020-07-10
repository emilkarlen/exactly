from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.test_case_utils.matcher.impls.run_program import sdv as run_pgm_sdv
from exactly_lib.test_case_utils.matcher.impls.run_program.runner import Runner
from exactly_lib.test_case_utils.program.execution import exe_wo_transformation
from exactly_lib.test_case_utils.program.execution.exe_wo_transformation import ExecutionResultAndStderr
from exactly_lib.test_case_utils.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.type_system.logic.program.program import Program
from exactly_lib.type_system.logic.string_matcher import StringMatcherSdv
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.util.process_execution import file_ctx_managers


def sdv(program: ProgramSdv) -> StringMatcherSdv:
    return run_pgm_sdv.sdv(_StringMatcherRunner, program)


class _StringMatcherRunner(Runner[StringModel]):
    def run(self, program_for_model: Program, model: StringModel) -> ExecutionResultAndStderr:
        path_of_file_with_model = model.as_file
        app_env = self._application_environment
        return exe_wo_transformation.execute(
            program_for_model,
            app_env.tmp_files_space.new_path_as_existing_dir(),
            app_env.os_services,
            app_env.process_execution_settings,
            file_ctx_managers.open_file(path_of_file_with_model, 'r'),
        )

    def program_for_model(self, matcher_argument_program: Program, model: StringModel) -> Program:
        return Program(
            matcher_argument_program.command,
            matcher_argument_program.stdin,
            IdentityStringTransformer(),
        )
