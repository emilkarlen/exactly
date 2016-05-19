import os
import pathlib
import shutil
import unittest

from exactly_lib import program_info
from exactly_lib.act_phase_setups import python3
from exactly_lib.execution import full_execution
from exactly_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from exactly_lib.execution.partial_execution import ScriptHandling
from exactly_lib.execution.result import FullResult
from exactly_lib.processing.processors import script_handling_for_setup
from exactly_lib.test_case import test_case_doc
from exactly_lib_test.execution.test_resources import utils


class FullExecutionTestCaseBase:
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False,
                 script_handling: ScriptHandling = None):
        self.__unittest_case = unittest_case
        self.__dbg_do_not_delete_dir_structure = dbg_do_not_delete_dir_structure
        self.__full_result = None
        self.__execution_directory_structure = None
        self.__initial_home_dir_path = None
        self.__script_handling = script_handling
        if self.__script_handling is None:
            self.__script_handling = script_handling_for_setup(python3.new_act_phase_setup())

    def execute(self):
        # SETUP #
        self.__initial_home_dir_path = pathlib.Path().resolve()
        # ACT #
        full_result = full_execution.execute(
                self.__script_handling,
                self._test_case(),
                self.initial_home_dir_path,
            program_info.PROGRAM_NAME + '-test-',
                True)

        # ASSERT #
        self.__full_result = full_result
        self._assertions()
        # CLEANUP #
        os.chdir(str(self.initial_home_dir_path))
        if not self.__dbg_do_not_delete_dir_structure and self.eds:
            shutil.rmtree(str(self.eds.root_dir))
        else:
            if self.eds:
                print(str(self.eds.root_dir))

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
    def eds(self) -> ExecutionDirectoryStructure:
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
