from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, TextIO

from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.program import top_lvl_error_msg_rendering
from exactly_lib.test_case_utils.program_execution.command_executor import CommandExecutor
from exactly_lib.test_case_utils.string_models.transformed_model_from_lines import \
    TransformedStringModelFromFileCreatedOnDemand
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.program.program import Program
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.util.process_execution import file_ctx_managers
from exactly_lib.util.process_execution.exe_store_and_read_stderr import ResultWithFiles, \
    ExecutorThatStoresResultInFilesInDirAndReadsStderrOnNonZeroExitCode
from exactly_lib.util.process_execution.process_executor import ProcessExecutor, ExecutableExecutor
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
                self._exit_code_handler(),
                self._program,
            ).create,
            model,
        )

    def _exit_code_handler(self) -> Callable[[int, Path], None]:
        return (
            _ignore_exit_code
            if self._ignore_exit_code
            else
            _HardErrorOnNonZeroExitCode(self._program,
                                        LimitedFileReader(),
                                        ).apply
        )


class _TransformedFileCreator:
    def __init__(self,
                 environment: ApplicationEnvironment,
                 exit_code_handler: Callable[[int, Path], None],
                 transformer: Program,
                 ):
        self.environment = environment
        self.exit_code_handler = exit_code_handler
        self.transformer = transformer

    def create(self, model: StringModel) -> Path:
        command_executor = self._command_executor(model)
        app_env = self.environment
        result = command_executor.execute(
            app_env.process_execution_settings,
            self.transformer.command,
            self.transformer.structure(),
        )
        self.exit_code_handler(result.exit_code,
                               result.files.path_of_std(ProcOutputFile.STDERR))

        return result.files.path_of_std(ProcOutputFile.STDOUT)

    def _command_executor(self, model: StringModel) -> CommandExecutor[ResultWithFiles]:
        return CommandExecutor(
            self.environment.os_services,
            self._executor(model)
        )

    def _executor(self, model: StringModel) -> ExecutableExecutor[ResultWithFiles]:
        path_of_file_with_model = model.as_file
        return ExecutorThatStoresResultInFilesInDirAndReadsStderrOnNonZeroExitCode(
            ProcessExecutor(),
            self.environment.tmp_files_space.new_path_as_existing_dir('str-trans-run'),
            file_ctx_managers.open_file(path_of_file_with_model, 'r'),
        )


class TextFilePartReader(ABC):
    @abstractmethod
    def read(self, f: TextIO) -> str:
        pass


class WholeFileReader(TextFilePartReader):
    def read(self, f: TextIO) -> str:
        return f.read()


class LimitedFileReader(TextFilePartReader):
    def __init__(self, limit: int = 1024):
        self._limit = limit

    def read(self, f: TextIO) -> str:
        chunk = f.read(self._limit)
        return (
            chunk
            if len(f.read(1)) == 0
            else
            chunk + '...'
        )


def _ignore_exit_code(exit_code: int, stderr: Path):
    pass


class _HardErrorOnNonZeroExitCode:
    def __init__(self,
                 program: Program,
                 err_msg_reader: TextFilePartReader,
                 ):
        self._program = program
        self._err_msg_reader = err_msg_reader

    def apply(self, exit_code: int, stderr: Path):
        if exit_code == 0:
            return

        stderr_contents = self._stderr_part(stderr)
        message_renderer = top_lvl_error_msg_rendering.non_zero_exit_code_msg(
            self._program.structure(),
            exit_code,
            stderr_contents,
        )
        raise HardErrorException(
            message_renderer
        )

    def _stderr_part(self, stderr: Path) -> str:
        with stderr.open() as f:
            return self._err_msg_reader.read(f)
