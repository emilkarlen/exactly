import pathlib

from shellcheck_lib.document.parse import SectionElementParser
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.general.output import StdOutputFiles
from shellcheck_lib.test_case.sections.act.script_source import ScriptSourceAccumulator, ScriptSourceBuilder
from shellcheck_lib.test_case.sections.result import svh


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
                 source: ScriptSourceBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        """
        Validates the given source.

        If success is not returned, then the test is aborted.
        """
        raise NotImplementedError()

    def prepare(self,
                source_setup: SourceSetup,
                eds: ExecutionDirectoryStructure):
        """
        Executed after validate.

        An opportunity to prepare for execution.

        E.g. write the source code to file.
        """
        raise NotImplementedError()

    def execute(self,
                source_setup: SourceSetup,
                cwd_dir_path: pathlib.Path,
                eds: ExecutionDirectoryStructure,
                stdin,
                std_output_files: StdOutputFiles) -> int:
        """
        Executed after prepare.
        :param cwd_dir_path: The directory that should be (initial) Current Working Directory of the program.
        :param stdin: A file object that should become stdin of the program.
        :param std_output_files: File objects that should become stdout and stderr of the program.
        """
        raise NotImplementedError()


class ActPhaseSetup:
    def __init__(self,
                 parser: SectionElementParser,
                 script_builder_constructor,
                 executor: ActProgramExecutor):
        """
        :param script_builder_constructor: () -> ScriptSourceBuilder
        """
        self.parser = parser
        self.script_builder_constructor = script_builder_constructor
        self.executor = executor
