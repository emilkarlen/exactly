from typing import IO

from exactly_lib.test_case_utils.program_execution import command_processors
from exactly_lib.test_case_utils.program_execution.command_processor import CommandProcessor
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.type_system.logic.program.program import Program
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.util.process_execution import file_ctx_managers, process_output_files
from exactly_lib.util.process_execution.executors import store_result_in_files
from exactly_lib.util.process_execution.executors.store_result_in_files import ExitCodeAndStderrFile
from . import transformed_string_models


def transformed_by_command(transformer: Command,
                           ignore_exit_code: bool,
                           environment: ApplicationEnvironment,
                           source_model: StringModel,
                           ) -> StringModel:
    return transformed_string_models.TransformedStringModelFromWriter(
        _TransformationWriter(
            environment,
            ignore_exit_code,
            transformer,
        ).write,
        source_model,
    )


def transformed_by_program(transformer: Program,
                           ignore_exit_code: bool,
                           environment: ApplicationEnvironment,
                           source_model: StringModel,
                           ) -> StringModel:
    initial_transformation = transformed_by_command(
        transformer.command,
        ignore_exit_code,
        environment, source_model
    )
    return (
        initial_transformation
        if transformer.transformation.is_identity_transformer
        else
        transformer.transformation.transform(initial_transformation)
    )


class _TransformationWriter:
    def __init__(self,
                 environment: ApplicationEnvironment,
                 ignore_exit_code: bool,
                 transformer: Command,
                 ):
        self.environment = environment
        self._ignore_exit_code = ignore_exit_code
        self.transformer = transformer

    def write(self, model: StringModel, output: IO):
        command_processor = self._command_processor(model, output)
        command_processor.process(
            self.environment.process_execution_settings,
            self.transformer,
        )

    def _command_processor(self, model: StringModel, output: IO) -> CommandProcessor[ExitCodeAndStderrFile]:
        return command_processors.processor_that_optionally_raises_hard_error_on_non_zero_exit_code(
            self._ignore_exit_code,
            self._exit_code_agnostic_processor(model, output),
            ExitCodeAndStderrFile.exit_code.fget,
            ExitCodeAndStderrFile.stderr.fget,
        )

    def _exit_code_agnostic_processor(self, model: StringModel, output: IO) -> CommandProcessor[ExitCodeAndStderrFile]:
        path_of_file_with_model = model.as_file
        return store_result_in_files.ProcessorThatStoresStderrInFiles(
            self.environment.os_services.command_executor,
            stdin=file_ctx_managers.open_file(path_of_file_with_model, 'r'),
            stdout=file_ctx_managers.opened_file(output),
            stderr_path_created_on_demand=
            self.environment.tmp_files_space.new_path(process_output_files.STDERR_FILE_NAME),
        )
