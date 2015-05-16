import os
import shutil
import pathlib
import unittest

from shelltest.exec_abs_syn import abs_syn_gen
from shelltest.execution.execution_directory_structure import ExecutionDirectoryStructure
from shelltest.execution.result import FullResult
from shelltest.script_language import python3
from shelltest.execution import full_execution
from shelltest_test.execution.util import utils


class FullExecutionTestCase:
    """
    Base class for tests on a test case that uses the Python 3 language in the apply phase.
    """

    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False):
        self.__unittest_case = unittest_case
        self.__dbg_do_not_delete_dir_structure = dbg_do_not_delete_dir_structure
        self.__full_result = None
        self.__execution_directory_structure = None

    def execute(self):
        # SETUP #
        home_dir_path = pathlib.Path().resolve()
        # ACT #
        full_result = full_execution.execute(
            python3.Python3ScriptFileManager(),
            python3.new_script_source_writer(),
            self._test_case(),
            home_dir_path,
            'shelltest-test-',
            True)

        # ASSERT #
        self.__full_result = full_result
        self._assertions()
        # CLEANUP #
        os.chdir(str(home_dir_path))
        if not self.__dbg_do_not_delete_dir_structure and self.eds:
            shutil.rmtree(str(self.eds.root_dir))
        else:
            if self.eds:
                print(str(self.eds.root_dir))

    def _test_case(self) -> abs_syn_gen.TestCase:
        raise NotImplementedError()

    def _assertions(self):
        raise NotImplementedError()

    @property
    def utc(self) -> unittest.TestCase:
        return self.__unittest_case

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
