from typing import TextIO

from exactly_lib.impls.program_execution import command_processors
from exactly_lib.impls.program_execution.command_processor import CommandProcessor
from exactly_lib.impls.program_execution.processors import store_result_in_files
from exactly_lib.impls.program_execution.processors.store_result_in_files import ExitCodeAndStderrFile
from exactly_lib.impls.types.program.run_program_description import RunProgramStructureRenderer
from exactly_lib.impls.types.string_transformer import sequence_resolving
from exactly_lib.impls.types.utils.command_w_stdin import CommandWStdin
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.type_val_prims.string_source.impls import concat
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.process_execution import file_ctx_managers, process_output_files
from . import transformed_string_sources


def transformed_by_command(structure_header: str,
                           transformer: CommandWStdin,
                           ignore_exit_code: bool,
                           environment: ApplicationEnvironment,
                           model: StringSource,
                           ) -> StringSource:
    def get_transformer_structure() -> StructureRenderer:
        return RunProgramStructureRenderer(
            structure_header,
            ignore_exit_code,
            transformer.structure,
        )

    model_w_stdin = concat.string_source_of_non_empty_sequence(
        list(transformer.stdin) + [model],
        environment.mem_buff_size,
    )
    return transformed_string_sources.transformed_string_source_from_writer(
        _TransformationWriter(
            environment,
            ignore_exit_code,
            transformer.command,
        ).write,
        model_w_stdin,
        get_transformer_structure,
        environment.mem_buff_size,
    )


def transformed_by_program(structure_header: str,
                           transformer: Program,
                           ignore_exit_code: bool,
                           environment: ApplicationEnvironment,
                           model: StringSource,
                           ) -> StringSource:
    initial_transformation = transformed_by_command(
        structure_header,
        CommandWStdin(transformer.command, transformer.stdin),
        ignore_exit_code,
        environment,
        model
    )
    transformation_of_program = sequence_resolving.resolve(transformer.transformation)
    return (
        initial_transformation
        if transformation_of_program.is_identity_transformer
        else
        transformation_of_program.transform(initial_transformation)
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

    def write(self, source: StringSourceContents, output: TextIO):
        command_processor = self._command_processor(source, output)
        command_processor.process(
            self.environment.process_execution_settings,
            self.transformer,
        )

    def _command_processor(self,
                           source: StringSourceContents,
                           output: TextIO) -> CommandProcessor[ExitCodeAndStderrFile]:
        return command_processors.processor_that_optionally_raises_hard_error_on_non_zero_exit_code(
            self._ignore_exit_code,
            self._exit_code_agnostic_processor(source, output),
            ExitCodeAndStderrFile.exit_code.fget,
            ExitCodeAndStderrFile.stderr.fget,
        )

    def _exit_code_agnostic_processor(self,
                                      source: StringSourceContents,
                                      output: TextIO) -> CommandProcessor[ExitCodeAndStderrFile]:
        path_of_file_with_model = source.as_file
        return store_result_in_files.ProcessorThatStoresStderrInFiles(
            self.environment.os_services.command_executor,
            stdin=file_ctx_managers.open_file(path_of_file_with_model, 'r'),
            stdout=file_ctx_managers.opened_file(output),
            stderr_path_created_on_demand=
            self.environment.tmp_files_space.new_path(process_output_files.STDERR_FILE_NAME),
        )
