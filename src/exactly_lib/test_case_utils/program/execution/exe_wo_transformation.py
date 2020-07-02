import pathlib
from typing import Optional

from exactly_lib.common.report_rendering.parts.failure_details import FailureDetailsRenderer
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.exception_detection import DetectedException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case_utils.program.top_lvl_error_msg_rendering import unable_to_execute_msg
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.program.program import Program
from exactly_lib.util.process_execution import sub_process_execution as spe, process_output_files
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.process_execution.process_output_files import FileNames
from exactly_lib.util.simple_textstruct.rendering import line_objects, blocks


class ExecutionResultAndStderr(tuple):
    """
    Result of an execution of a sub process

    Contents of stderr is included, if exit code is non zero.
    """

    def __new__(cls,
                exit_code: int,
                stderr_contents: Optional[str],
                output_dir_path: pathlib.Path,
                program: StructureRenderer,
                ):
        return tuple.__new__(cls, (exit_code,
                                   stderr_contents,
                                   output_dir_path,
                                   program))

    @property
    def exit_code(self) -> int:
        return self[0]

    @property
    def stderr_contents(self) -> Optional[str]:
        return self[1]

    @property
    def output_dir_path(self) -> pathlib.Path:
        return self[2]

    @property
    def program(self) -> StructureRenderer:
        return self[3]

    @property
    def file_names(self) -> FileNames:
        return process_output_files.FILE_NAMES

    def path_of(self, output_file: process_output_files.ProcOutputFile) -> pathlib.Path:
        return self.output_dir_path / self.file_names.name_of(output_file)


def execute(program: Program,
            output_dir: pathlib.Path,
            os_services: OsServices,
            settings: ProcessExecutionSettings
            ) -> ExecutionResultAndStderr:
    """
    Executes the program, ignoring any transformations.

    :param program: The program to execute. Any transformations are ignored.
    :param output_dir: Stores the output from the program - exit-code, stdout, stderr.
    Must be an existing, writable, directory.

    :returns ExecutionResultAndStderr: Contents of stderr is included iff exit-code is non-zero.
    :raises HardErrorException: Program cannot be executed.
    """
    executor = spe.ExecutorThatStoresResultInFilesInDir(settings)
    try:
        executable = os_services.executable_factory__detect_ex().make(program.command)
        result_and_std_err = spe.execute_and_read_stderr_if_non_zero_exitcode(executable, executor, output_dir)
        if not result_and_std_err.result.is_success:
            raise HardErrorException(
                unable_to_execute_msg(program.structure(),
                                      _string_major_blocks(result_and_std_err.result.error_message))
            )
        return ExecutionResultAndStderr(
            result_and_std_err.result.exit_code,
            result_and_std_err.stderr_contents,
            output_dir,
            program.structure(),
        )
    except DetectedException as ex:
        raise HardErrorException(
            unable_to_execute_msg(program.structure(),
                                  FailureDetailsRenderer(ex.failure_details))
        )


def _string_major_blocks(s: str) -> TextRenderer:
    return blocks.MajorBlocksOfSingleLineObject(
        line_objects.PreFormattedString.of_str(s)
    )
