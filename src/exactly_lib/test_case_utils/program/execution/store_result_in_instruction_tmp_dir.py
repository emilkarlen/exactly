import pathlib

from exactly_lib.test_case.exception_detection import DetectedException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, InstructionSourceInfo, \
    instruction_log_dir
from exactly_lib.test_case_utils import pfh_exception
from exactly_lib.test_case_utils.file_creation import FileTransformerHelper
from exactly_lib.type_system.logic.program.program import Program
from exactly_lib.util.file_utils.tmp_file_space import TmpDirFileSpace
from exactly_lib.util.process_execution import process_output_files
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.process_execution.sub_process_execution import ExecutorThatStoresResultInFilesInDir, Result


class ResultWithTransformation:
    def __init__(self,
                 process_result: Result,
                 file_with_transformed_contents: str
                 ):
        self.process_result = process_result
        self.file_with_transformed_contents = file_with_transformed_contents

    @property
    def path_of_file_with_transformed_contents(self) -> pathlib.Path:
        return self.process_result.output_dir_path / self.file_with_transformed_contents


def make_transformed_file_from_output_in_instruction_tmp_dir(environment: InstructionEnvironmentForPostSdsStep,
                                                             os_services: OsServices,
                                                             source_info: InstructionSourceInfo,
                                                             checked_output: process_output_files.ProcOutputFile,
                                                             program: Program) -> ResultWithTransformation:
    """
    :raises PfhHardErrorException: IO error.
    """
    return make_transformed_file_from_output(instruction_log_dir(environment.phase_logging, source_info),
                                             environment.process_execution_settings,
                                             os_services,
                                             environment.tmp_file_space,
                                             checked_output,
                                             program)


def make_transformed_file_from_output(pgm_output_dir: pathlib.Path,
                                      process_execution_settings: ProcessExecutionSettings,
                                      os_services: OsServices,
                                      tmp_file_space: TmpDirFileSpace,
                                      transformed_output: process_output_files.ProcOutputFile,
                                      program: Program,
                                      ) -> ResultWithTransformation:
    """
    :raises PfhHardErrorException: IO error.
    """
    executor = ExecutorThatStoresResultInFilesInDir(process_execution_settings)

    try:
        executable = os_services.executable_factory__detect_ex().make(program.command)
    except DetectedException as ex:
        raise pfh_exception.PfhHardErrorException(ex.failure_details.failure_message)

    result = executor.execute(pgm_output_dir, executable)
    if program.transformation.is_identity_transformer:
        return ResultWithTransformation(result,
                                        result.file_names.name_of(transformed_output))

    transformation_helper = FileTransformerHelper(
        os_services,
        tmp_file_space,
    )
    result_path = result.output_dir_path / (result.file_names.name_of(transformed_output) + '-transformed')
    error_message = transformation_helper.transform_to_file(result.path_of(transformed_output),
                                                            result_path,
                                                            program.transformation)
    if error_message is not None:
        raise pfh_exception.PfhHardErrorException(error_message)

    return ResultWithTransformation(result,
                                    result_path.name)
