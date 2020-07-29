from pathlib import Path

from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.program_execution import command_processors, command_executors
from exactly_lib.test_case_utils.program_execution.command_processor import CommandProcessor
from exactly_lib.test_case_utils.string_transformer.impl.transformed_string_models import \
    TransformedStringModelFromFileCreatedOnDemand
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.program.program import Program
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.util.process_execution import file_ctx_managers
from exactly_lib.util.process_execution.executors import store_result_in_files
from exactly_lib.util.process_execution.executors.store_result_in_files import ExitCodeAndFiles
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile


def transformer(name: str,
                environment: ApplicationEnvironment,
                ignore_exit_code: bool,
                program: Program,
                structure: StructureRenderer,
                ) -> StringTransformer:
    return _RunStringTransformer(
        name,
        environment,
        ignore_exit_code,
        program,
        structure,
    )


class _RunStringTransformer(WithCachedTreeStructureDescriptionBase, StringTransformer):
    def __init__(self,
                 name: str,
                 environment: ApplicationEnvironment,
                 ignore_exit_code: bool,
                 program: Program,
                 structure: StructureRenderer,
                 ):
        super().__init__()
        self._name = name
        self._environment = environment
        self._ignore_exit_code = ignore_exit_code
        self._program = program
        self._structure = structure

    @property
    def name(self) -> str:
        return self._name

    def _structure(self) -> StructureRenderer:
        return self._structure

    def transform(self, model: StringModel) -> StringModel:
        process_transformation = self._process_transformation(model)
        return (
            process_transformation
            if self._program.transformation.is_identity_transformer
            else
            self._program.transformation.transform(process_transformation)
        )

    def _process_transformation(self, model: StringModel) -> StringModel:
        return TransformedStringModelFromFileCreatedOnDemand(
            _TransformedFileCreator(
                self._environment,
                self._ignore_exit_code,
                self._program,
            ).create,
            model,
        )


class _TransformedFileCreator:
    def __init__(self,
                 environment: ApplicationEnvironment,
                 ignore_exit_code: bool,
                 transformer: Program,
                 ):
        self.environment = environment
        self._ignore_exit_code = ignore_exit_code
        self.transformer = transformer

    def create(self, model: StringModel) -> Path:
        command_processor = self._command_processor(model)
        app_env = self.environment
        result = command_processor.process(
            app_env.process_execution_settings,
            self.transformer.command,
        )

        return result.files.path_of_std(ProcOutputFile.STDOUT)

    def _command_processor(self, model: StringModel) -> CommandProcessor[ExitCodeAndFiles]:
        return command_processors.processor_that_optionally_raises_hard_error_on_non_zero_exit_code(
            self._ignore_exit_code,
            self._exit_code_agnostic_processor(model),
            ExitCodeAndFiles.exit_code.fget,
            ExitCodeAndFiles.stderr_file.fget,
        )

    def _exit_code_agnostic_processor(self, model: StringModel) -> CommandProcessor[ExitCodeAndFiles]:
        path_of_file_with_model = model.as_file
        return store_result_in_files.ProcessorThatStoresResultInFilesInDir(
            command_executors.command_executor(self.environment.os_services),
            self.environment.tmp_files_space.new_path_as_existing_dir('str-trans-run'),
            file_ctx_managers.open_file(path_of_file_with_model, 'r'),
        )
