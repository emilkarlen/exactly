import os
import pathlib
import shutil
import unittest

from exactly_lib import program_info
from exactly_lib.act_phase_setups.script_interpretation import python3
from exactly_lib.execution import full_execution
from exactly_lib.execution.result import FullResult
from exactly_lib.processing.processors import act_phase_handling_for_setup
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.execution.test_resources import utils


class FullExecutionTestCaseBase:
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False,
                 act_phase_handling: ActPhaseHandling = None):
        self.__unittest_case = unittest_case
        self.__dbg_do_not_delete_dir_structure = dbg_do_not_delete_dir_structure
        self.__full_result = None
        self.__execution_directory_structure = None
        self.__initial_home_dir_path = None
        self.__act_phase_handling = act_phase_handling

    def execute(self):
        # SETUP #
        self.__initial_home_dir_path = pathlib.Path().resolve()
        # ACT #
        full_result = full_execution.execute(
            self._test_case(),
            ConfigurationBuilder(self.initial_home_dir_path.resolve(),
                                 self._act_phase_handling()),
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
            return act_phase_handling_for_setup(python3.new_act_phase_setup())
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
        return self.__full_result.execution_directory_structure

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
