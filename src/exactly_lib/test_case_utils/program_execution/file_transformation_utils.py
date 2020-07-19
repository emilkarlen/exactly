import pathlib

from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils import pfh_exception
from exactly_lib.test_case_utils.file_creation import FileTransformerHelper
from exactly_lib.test_case_utils.program_execution import command_executors
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.program.program import Program
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.process_execution import process_output_files, file_ctx_managers
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.process_execution.executors import store_result_in_files
from exactly_lib.util.process_execution.executors.store_result_in_files import ExitCodeAndFiles
from exactly_lib.util.process_execution.process_executor import ProcessExecutor


class ResultWithTransformation:
    def __init__(self,
                 process_result: ExitCodeAndFiles,
                 file_with_transformed_contents: str
                 ):
        self.process_result = process_result
        self.file_with_transformed_contents = file_with_transformed_contents

    @property
    def path_of_file_with_transformed_contents(self) -> pathlib.Path:
        return self.process_result.files.directory / self.file_with_transformed_contents


def make_transformed_file_from_output_in_instruction_tmp_dir(environment: InstructionEnvironmentForPostSdsStep,
                                                             os_services: OsServices,
                                                             checked_output: process_output_files.ProcOutputFile,
                                                             program: Program) -> ResultWithTransformation:
    """
    :raises PfhHardErrorException: IO error.
    """
    storage_dir = environment.tmp_dir__path_access.root_dir__existing
    return make_transformed_file_from_output(storage_dir,
                                             environment.proc_exe_settings,
                                             os_services,
                                             environment.tmp_dir__path_access.paths_access,
                                             checked_output,
                                             program)


def make_transformed_file_from_output(pgm_output_dir: pathlib.Path,
                                      process_execution_settings: ProcessExecutionSettings,
                                      os_services: OsServices,
                                      tmp_file_space: DirFileSpace,
                                      transformed_output: process_output_files.ProcOutputFile,
                                      program: Program,
                                      ) -> ResultWithTransformation:
    """
    :raises PfhHardErrorException: IO error.
    """
    cmd_exe = command_executors.executor_that_raises_hard_error(
        os_services,
        store_result_in_files.ExecutorThatStoresResultInFilesInDir(
            ProcessExecutor(), pgm_output_dir,
            file_ctx_managers.dev_null(),
        )
    )

    try:
        result = cmd_exe.execute(process_execution_settings,
                                 program.command,
                                 program.structure())
    except HardErrorException as ex:
        raise pfh_exception.PfhHardErrorException(ex.error)

    if program.transformation.is_identity_transformer:
        return ResultWithTransformation(result,
                                        result.files.base_name_of(transformed_output))

    transformation_helper = FileTransformerHelper(
        os_services,
        tmp_file_space,
    )
    base_name_of_path_of_transformed_output = result.files.base_name_of(transformed_output) + '-transformed'
    result_path = pgm_output_dir / base_name_of_path_of_transformed_output
    error_message = transformation_helper.transform_to_file(result.files.path_of_std(transformed_output),
                                                            result_path,
                                                            program.transformation)
    if error_message is not None:
        raise pfh_exception.PfhHardErrorException(error_message)

    return ResultWithTransformation(result,
                                    base_name_of_path_of_transformed_output)
