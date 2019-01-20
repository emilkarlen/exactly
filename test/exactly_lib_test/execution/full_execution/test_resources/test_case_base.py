import unittest

import os
import pathlib
import shutil

from exactly_lib.actors.source_interpreter import python3
from exactly_lib.execution.configuration import ExecutionConfiguration
from exactly_lib.execution.full_execution import execution
from exactly_lib.execution.full_execution.result import FullExeResult
from exactly_lib.test_case import test_case_doc, os_services
from exactly_lib.test_case.actor import AtcOsProcessExecutor, Actor
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.execution.test_resources import utils, sandbox_root_name_resolver


class FullExecutionTestCaseBase:
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False,
                 actor: Actor = None,
                 atc_os_process_executor: AtcOsProcessExecutor =
                 os_services.DEFAULT_ATC_OS_PROCESS_EXECUTOR):
        self.__unittest_case = unittest_case
        self.__dbg_do_not_delete_dir_structure = dbg_do_not_delete_dir_structure
        self.__full_result = None
        self.__sandbox_directory_structure = None
        self.__initial_home_dir_path = None
        self.__actor = actor
        self.__atc_os_process_executor = atc_os_process_executor

    def execute(self):
        # SETUP #
        self.__initial_home_dir_path = pathlib.Path().resolve()
        # ACT #
        initial_home_dir_path = self.initial_home_dir_path.resolve()
        exe_conf = ExecutionConfiguration(dict(os.environ),
                                          self.__atc_os_process_executor,
                                          sandbox_root_name_resolver.for_test(),
                                          SymbolTable())
        configuration_builder = ConfigurationBuilder(initial_home_dir_path,
                                                     initial_home_dir_path,
                                                     self._actor())
        full_result = execution.execute(
            exe_conf,
            configuration_builder,
            True,
            self._test_case())

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

    def _actor(self) -> Actor:
        if self.__actor is None:
            return python3.new_actor()
        return self.__actor

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
    def full_result(self) -> FullExeResult:
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
