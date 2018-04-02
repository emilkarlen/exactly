import pathlib

from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhHardErrorException
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, InstructionSourceInfo, \
    instruction_log_dir
from exactly_lib.test_case_utils.external_program.program import Program
from exactly_lib.test_case_utils.file_creation import create_file_from_transformation_of_existing_file
from exactly_lib.test_case_utils.sub_proc.sub_process_execution import ExecutorThatStoresResultInFilesInDir
from exactly_lib.util.process_execution import process_output_files


def make_transformed_file_from_output_in_instruction_tmp_dir(environment: InstructionEnvironmentForPostSdsStep,
                                                             source_info: InstructionSourceInfo,
                                                             checked_output: process_output_files.ProcOutputFile,
                                                             program: Program) -> pathlib.Path:
    """
    :raises PfhHardErrorException: IO error.
    """
    executor = ExecutorThatStoresResultInFilesInDir(environment.process_execution_settings)
    storage_dir = instruction_log_dir(environment.phase_logging, source_info)

    result = executor.apply(storage_dir, program.command)
    if program.transformation.is_identity_transformer:
        return result.path_of(checked_output)

    result_path = result.output_dir_path / (result.file_names.name_of(checked_output) + '-transformed')
    error_message = create_file_from_transformation_of_existing_file(result.path_of(checked_output),
                                                                     result_path,
                                                                     program.transformation)
    if error_message is not None:
        raise PfhHardErrorException(error_message)

    return result_path
