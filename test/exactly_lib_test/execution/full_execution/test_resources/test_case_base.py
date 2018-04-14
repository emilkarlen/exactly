import os
import pathlib
import shutil
import unittest

from exactly_lib import program_info
from exactly_lib.act_phase_setups.source_interpreter import python3
from exactly_lib.execution import full_execution
from exactly_lib.execution.full_execution import PredefinedProperties
from exactly_lib.execution.result import FullResult
from exactly_lib.test_case import test_case_doc, os_services
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling, ActPhaseOsProcessExecutor
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.execution.test_resources import utils


class FullExecutionTestCaseBase:
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False,
                 act_phase_handling: ActPhaseHandling = None,
                 act_phase_os_process_executor: ActPhaseOsProcessExecutor = os_services.DEFAULT_ACT_PHASE_OS_PROCESS_EXECUTOR):
        self.__unittest_case = unittest_case
        self.__dbg_do_not_delete_dir_structure = dbg_do_not_delete_dir_structure
        self.__full_result = None
        self.__sandbox_directory_structure = None
        self.__initial_home_dir_path = None
        self.__act_phase_handling = act_phase_handling
        self.__act_phase_os_process_executor = act_phase_os_process_executor

    def execute(self):
        # SETUP #
        self.__initial_home_dir_path = pathlib.Path().resolve()
        # ACT #
        initial_home_dir_path = self.initial_home_dir_path.resolve()
        full_result = full_execution.execute(
            self._test_case(),
            PredefinedProperties(),
            ConfigurationBuilder(initial_home_dir_path,
                                 initial_home_dir_path,
                                 self._act_phase_handling()),
            self.__act_phase_os_process_executor,
            program_info.PROGRAM_NAME + '-test-',
            True)

        # ASSERT #
        self.__full_result = full_result
        self._assertions()
        # CLEANUP #
        os.chdir(str(self.initial_home_dir_path))
        if not self.__dbg_do_not_delete_dir_structure and self.sds:
            shutil.rmtree(str(self.sds.root_dir))
        else:
            if self.sds:
                print(str(self.sds.root_dir))

    def _act_phase_handling(self) -> ActPhaseHandling:
        if self.__act_phase_handling is None:
            return python3.new_act_phase_handling()
        return self.__act_phase_handling

    def _test_case(self) -> test_case_doc.TestCase:
        raise NotImplementedError()

    def _assertions(self):
        raise NotImplementedError()

    @property
    def utc(self) -> unittest.TestCase:
        return self.__unittest_case

    @property
    def initial_home_dir_path(self) -> pathlib.Path:
        return self.__initial_home_dir_path

    @property
    def full_result(self) -> FullResult:
        return self.__full_result

    @property
    def sds(self) -> SandboxDirectoryStructure:
        return self.__full_result.sds

    def assert_is_regular_file_with_contents(self,
                                             path: pathlib.Path,
                                             expected_contents: str,
                                             msg=None):
        """
        Helper for test cases that check the contents of files.
        """
        utils.assert_is_file_with_contents(self.utc,
                                           path,
                                           expected_contents,
                                           msg)
