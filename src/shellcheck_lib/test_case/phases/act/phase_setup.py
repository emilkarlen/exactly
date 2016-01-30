import pathlib
import types

from shellcheck_lib.document.parse import SectionElementParser
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.general.std import StdFiles
from shellcheck_lib.test_case.phases.act.script_source import ScriptSourceAccumulator, ScriptSourceBuilder
from shellcheck_lib.test_case.phases.result import svh


class PhaseEnvironmentForScriptGeneration:
    """
    The phase-environment for phases that generate a script.
    """

    def __init__(self,
                 script_source_accumulator: ScriptSourceAccumulator):
        self.__script_source_accumulator = script_source_accumulator

    @property
    def append(self) -> ScriptSourceAccumulator:
        return self.__script_source_accumulator


class SourceSetup:
    def __init__(self,
                 script_builder: ScriptSourceBuilder,
                 script_output_dir_path: pathlib.Path,
                 script_file_stem: str):
        self.script_builder = script_builder
        self.script_output_dir_path = script_output_dir_path
        self.script_file_stem = script_file_stem


class ActProgramExecutor:
    def validate(self,
                 home_dir: pathlib.Path,
                 source: ScriptSourceBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        """
        Validates the given source.

        If success is not returned, then the test is aborted.
        """
        raise NotImplementedError()

    def prepare(self,
                source_setup: SourceSetup,
                home_dir_path: pathlib.Path,
                eds: ExecutionDirectoryStructure):
        """
        Executed after validate.

        An opportunity to prepare for execution.

        E.g. write the source code to file.
        """
        raise NotImplementedError()

    def execute(self,
                source_setup: SourceSetup,
                home_dir: pathlib.Path,
                eds: ExecutionDirectoryStructure,
                std_files: StdFiles) -> int:
        """
        Executed after prepare.

        :returns exit code of executed program
        """
        raise NotImplementedError()


class ActPhaseSetup(tuple):
    def __new__(cls,
                parser: SectionElementParser,
                script_builder_constructor,
                executor: ActProgramExecutor):
        """
        :param script_builder_constructor: () -> ScriptSourceBuilder
        """
        return tuple.__new__(cls, (parser,
                                   script_builder_constructor,
                                   executor))

    @property
    def parser(self) -> SectionElementParser:
        return self[0]

    @property
    def script_builder_constructor(self) -> types.FunctionType:
        """
        :return: () -> ScriptSourceBuilder
        """
        return self[1]

    @property
    def executor(self) -> ActProgramExecutor:
        return self[2]
