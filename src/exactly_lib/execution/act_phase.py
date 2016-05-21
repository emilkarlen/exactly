import pathlib

from exactly_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from exactly_lib.test_case.phases.act.program_source import ActSourceBuilder
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.std import StdFiles


class SourceSetup:
    def __init__(self,
                 script_builder: ActSourceBuilder,
                 script_output_dir_path: pathlib.Path,
                 script_file_stem: str):
        self.script_builder = script_builder
        self.script_output_dir_path = script_output_dir_path
        self.script_file_stem = script_file_stem


class ActSourceExecutor:
    def validate(self,
                 home_dir: pathlib.Path,
                 source: ActSourceBuilder) -> svh.SuccessOrValidationErrorOrHardError:
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
