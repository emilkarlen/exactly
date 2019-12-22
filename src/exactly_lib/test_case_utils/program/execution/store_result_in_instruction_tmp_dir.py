import pathlib

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.test_case.executable_factory import ExecutableFactory
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, InstructionSourceInfo, \
    instruction_log_dir
from exactly_lib.test_case_utils import pfh_exception
from exactly_lib.test_case_utils.file_creation import create_file_from_transformation_of_existing_file
from exactly_lib.type_system.logic.program.program import Program
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
                                                             executable_factory: ExecutableFactory,
                                                             source_info: InstructionSourceInfo,
                                                             checked_output: process_output_files.ProcOutputFile,
                                                             program: Program) -> ResultWithTransformation:
    """
    :raises PfhHardErrorException: IO error.
    """
    return make_transformed_file_from_output(instruction_log_dir(environment.phase_logging, source_info),
                                             environment.process_execution_settings,
                                             executable_factory,
                                             checked_output,
                                             program)


def make_transformed_file_from_output(pgm_output_dir: pathlib.Path,
                                      process_execution_settings: ProcessExecutionSettings,
                                      executable_factory: ExecutableFactory,
                                      transformed_output: process_output_files.ProcOutputFile,
                                      program: Program) -> ResultWithTransformation:
    """
    :raises PfhHardErrorException: IO error.
    """
    executor = ExecutorThatStoresResultInFilesInDir(process_execution_settings)

    executable = executable_factory.make(program.command)
    result = executor.execute(pgm_output_dir, executable)
    if program.transformation.is_identity_transformer:
        return ResultWithTransformation(result,
                                        result.file_names.name_of(transformed_output))

    result_path = result.output_dir_path / (result.file_names.name_of(transformed_output) + '-transformed')
    error_message = create_file_from_transformation_of_existing_file(result.path_of(transformed_output),
                                                                     result_path,
                                                                     program.transformation)
    if error_message is not None:
        raise pfh_exception.PfhHardErrorException(text_docs.single_pre_formatted_line_object(error_message))

    return ResultWithTransformation(result,
                                    result_path.name)
