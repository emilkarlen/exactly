from exactly_lib.test_case_utils.file_matcher.impl.run_program.arguments_generator import ArgumentsGenerator
from exactly_lib.test_case_utils.matcher.impls.run_program.runner import Runner
from exactly_lib.test_case_utils.program.execution import exe_wo_transformation
from exactly_lib.test_case_utils.program.execution.exe_wo_transformation import ExecutionResultAndStderr
from exactly_lib.test_case_utils.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.program.process_execution import command
from exactly_lib.type_system.logic.program.program import Program
from exactly_lib.util.process_execution import file_ctx_managers


class FileMatcherRunner(Runner[FileMatcherModel]):
    def __init__(self,
                 args_generator: ArgumentsGenerator,
                 application_environment: ApplicationEnvironment,
                 ):
        super().__init__(application_environment)
        self._args_generator = args_generator

    def run(self, program_for_model: Program, model: FileMatcherModel) -> ExecutionResultAndStderr:
        app_env = self._application_environment
        return exe_wo_transformation.execute(
            program_for_model,
            app_env.tmp_files_space.new_path_as_existing_dir(),
            app_env.os_services,
            app_env.process_execution_settings,
            file_ctx_managers.dev_null(),
        )

    def program_for_model(self, matcher_argument_program: Program, model: FileMatcherModel) -> Program:
        original_command = matcher_argument_program.command
        arguments = self._args_generator.generate(original_command.arguments, str(model.path.primitive))
        command_for_model = command.Command(
            original_command.driver,
            arguments
        )
        return Program(
            command_for_model,
            matcher_argument_program.stdin,
            IdentityStringTransformer(),
        )
