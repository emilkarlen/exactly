import pathlib

from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhHardErrorException
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, InstructionSourceInfo, \
    instruction_log_dir
from exactly_lib.test_case_utils.external_program.program import Program
from exactly_lib.test_case_utils.file_creation import create_file_from_transformation_of_existing_file
from exactly_lib.test_case_utils.sub_proc.sub_process_execution import ExecutorThatStoresResultInFilesInDir


def make_transformed_file_from_output_in_instruction_tmp_dir(environment: InstructionEnvironmentForPostSdsStep,
                                                             source_info: InstructionSourceInfo,
                                                             program: Program) -> pathlib.Path:
    """
    :raises PfhHardErrorException: IO error.
    """
    executor = ExecutorThatStoresResultInFilesInDir(environment.process_execution_settings)
    storage_dir = instruction_log_dir(environment.phase_logging, source_info)

    result = executor.apply(storage_dir, program.command)
    if program.transformation.is_identity_transformer:
        return result.path_of_stdout

    result_path = result.output_dir_path / 'transformed'
    error_message = create_file_from_transformation_of_existing_file(result.path_of_stdout,
                                                                     result_path,
                                                                     program.transformation)
    if error_message is not None:
        raise PfhHardErrorException(error_message)

    return result_path
