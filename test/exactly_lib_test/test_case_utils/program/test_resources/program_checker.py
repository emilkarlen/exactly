import unittest

from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.test_case import executable_factories
from exactly_lib.test_case_utils.program.execution import store_result_in_instruction_tmp_dir as pgm_execution
from exactly_lib.type_system.logic.program.program import Program, ProgramDdv
from exactly_lib.util import file_utils
from exactly_lib.util.process_execution import execution_elements
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.test_case_utils.logic.test_resources.common_properties_checker import \
    CommonPropertiesConfiguration, Applier
from exactly_lib_test.test_case_utils.logic.test_resources.logic_type_checker import LogicSdvPropertiesChecker, \
    WithTreeStructureExecutionPropertiesChecker
from exactly_lib_test.test_case_utils.program.test_resources.assertions import ResultWithTransformationData
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder


class ProgramPropertiesConfiguration(
    CommonPropertiesConfiguration[Program,
                                  ProcOutputFile,
                                  ResultWithTransformationData]):
    def __init__(self):
        self._applier = _Applier()

    def applier(self) -> Applier[Program, ProcOutputFile, ResultWithTransformationData]:
        return self._applier

    def new_sdv_checker(self) -> LogicSdvPropertiesChecker[Program]:
        return LogicSdvPropertiesChecker(ProgramSdv)

    def new_execution_checker(self) -> WithTreeStructureExecutionPropertiesChecker:
        return WithTreeStructureExecutionPropertiesChecker(ProgramDdv, Program)


class _Applier(Applier[Program, ProcOutputFile, ResultWithTransformationData]):
    def apply(self,
              put: unittest.TestCase,
              message_builder: MessageBuilder,
              primitive: Program,
              resolving_environment: FullResolvingEnvironment,
              input_: ProcOutputFile) -> ResultWithTransformationData:
        executable_factory = executable_factories.get_factory_for_current_operating_system()
        process_execution_settings = execution_elements.with_no_timeout()

        pgm_output_dir = resolving_environment.application_environment.tmp_files_space.new_path_as_existing_dir()
        execution_result = pgm_execution.make_transformed_file_from_output(pgm_output_dir,
                                                                           process_execution_settings,
                                                                           executable_factory,
                                                                           input_,
                                                                           primitive)
        proc_exe_result = execution_result.process_result
        stderr_contents = file_utils.contents_of(proc_exe_result.path_of(ProcOutputFile.STDERR))
        stdout_contents = file_utils.contents_of(proc_exe_result.path_of(ProcOutputFile.STDOUT))
        result_of_transformation = file_utils.contents_of(execution_result.path_of_file_with_transformed_contents)
        proc_result_data = SubProcessResult(proc_exe_result.exit_code,
                                            stdout_contents,
                                            stderr_contents)
        return ResultWithTransformationData(proc_result_data,
                                            result_of_transformation)
