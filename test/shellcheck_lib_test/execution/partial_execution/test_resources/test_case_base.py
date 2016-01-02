import os
import pathlib
import shutil
import unittest

from shellcheck_lib.act_phase_setups import python3
from shellcheck_lib.default.execution_mode.test_case.processing import script_handling_for_setup
from shellcheck_lib.execution import partial_execution
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.execution.partial_execution import ScriptHandling, TestCase
from shellcheck_lib.execution.result import PartialResult
from shellcheck_lib_test.execution.test_resources import utils


class PartialExecutionTestCaseBase:
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False,
                 script_handling: ScriptHandling = None):
        self.__unittest_case = unittest_case
        self.__dbg_do_not_delete_dir_structure = dbg_do_not_delete_dir_structure
        self.__partial_result = None
        self.__execution_directory_structure = None
        self.__initial_home_dir_path = None
        self.__script_handling = script_handling
        if self.__script_handling is None:
            self.__script_handling = script_handling_for_setup(python3.new_act_phase_setup())

    def execute(self):
        # SETUP #
        self.__initial_home_dir_path = pathlib.Path().resolve()
        # ACT #
        partial_result = partial_execution.execute(
                self.__script_handling,
                self._test_case(),
                self.initial_home_dir_path,
                'shellcheck-test-',
                self.__dbg_do_not_delete_dir_structure)

        # ASSERT #
        self.__partial_result = partial_result
        self._assertions()
        # CLEANUP #
        os.chdir(str(self.initial_home_dir_path))
        if not self.__dbg_do_not_delete_dir_structure and self.eds:
            if self.eds.root_dir.exists():
                shutil.rmtree(str(self.eds.root_dir))
        else:
            if self.eds:
                print(str(self.eds.root_dir))

    def _test_case(self) -> TestCase:
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
    def partial_result(self) -> PartialResult:
        return self.__partial_result

    @property
    def eds(self) -> ExecutionDirectoryStructure:
        return self.__partial_result.execution_directory_structure

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
