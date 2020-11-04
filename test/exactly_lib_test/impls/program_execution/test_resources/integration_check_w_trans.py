import unittest

from exactly_lib.impls.os_services import os_services_access
from exactly_lib.impls.program_execution import file_transformation_utils as pgm_execution
from exactly_lib.impls.types.program.parse import parse_program
from exactly_lib.type_val_deps.envs.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.util.file_utils import misc_utils
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.impls.types.logic.test_resources.integration_check import IntegrationChecker
from exactly_lib_test.impls.types.program.test_resources import integration_check_config
from exactly_lib_test.impls.types.program.test_resources.assertions import ResultWithTransformationData
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_val_deps.dep_variants.test_resources.full_deps.common_properties_checker import \
    Applier
from exactly_lib_test.util.process_execution.test_resources.proc_exe_env import proc_exe_env_for_test


class _ExecutionAndTransformationApplier(Applier[Program, ProcOutputFile, ResultWithTransformationData]):
    def apply(self,
              put: unittest.TestCase,
              message_builder: MessageBuilder,
              primitive: Program,
              resolving_environment: FullResolvingEnvironment,
              input_: ProcOutputFile,
              ) -> ResultWithTransformationData:
        process_execution_settings = proc_exe_env_for_test(timeout_in_seconds=5)

        pgm_output_dir = resolving_environment.application_environment.tmp_files_space.new_path_as_existing_dir()
        execution_result = pgm_execution.make_transformed_file_from_output(pgm_output_dir,
                                                                           process_execution_settings,
                                                                           os_services_access.new_for_current_os(),
                                                                           resolving_environment.application_environment.tmp_files_space,
                                                                           input_,
                                                                           primitive)
        proc_exe_result = execution_result.process_result
        stderr_contents = misc_utils.contents_of(proc_exe_result.files.path_of_std(ProcOutputFile.STDERR))
        stdout_contents = misc_utils.contents_of(proc_exe_result.files.path_of_std(ProcOutputFile.STDOUT))
        result_of_transformation = misc_utils.contents_of(execution_result.path_of_file_with_transformed_contents)
        proc_result_data = SubProcessResult(proc_exe_result.exit_code,
                                            stdout_contents,
                                            stderr_contents)
        return ResultWithTransformationData(proc_result_data,
                                            result_of_transformation)


CHECKER_W_TRANSFORMATION = IntegrationChecker(
    parse_program.program_parser(),
    integration_check_config.ProgramPropertiesConfiguration(
        _ExecutionAndTransformationApplier()
    ),
    True,
)
