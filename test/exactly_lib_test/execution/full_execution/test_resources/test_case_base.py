import os
import pathlib
import shutil
import unittest
from typing import Optional, Mapping

from exactly_lib.execution.configuration import ExecutionConfiguration
from exactly_lib.execution.full_execution import execution
from exactly_lib.execution.full_execution.result import FullExeResult
from exactly_lib.execution.predefined_properties import os_environ_getter
from exactly_lib.impls.os_services import os_services_access
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.act.actor import Actor
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.test_case.phases.environ import DefaultEnvironGetter
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.execution.test_resources import utils, sandbox_root_name_resolver
from exactly_lib_test.impls.actors.test_resources import python3


class FullExecutionTestCaseBase:
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False,
                 actor: Actor = None,
                 default_environ_getter: DefaultEnvironGetter = os_environ_getter,
                 environ: Optional[Mapping[str, str]] = None,
                 os_services: OsServices = os_services_access.new_for_current_os(),
                 ):
        self.__unittest_case = unittest_case
        self.__dbg_do_not_delete_dir_structure = dbg_do_not_delete_dir_structure
        self.__full_result = None
        self.__sandbox_directory_structure = None
        self.__initial_hds_dir_path = None
        self.__actor = actor
        self.__os_services = os_services
        self.__default_environ_getter = default_environ_getter
        self.__environ = environ

    def execute(self):
        # SETUP #
        self.__initial_hds_dir_path = pathlib.Path().resolve()
        # ACT #
        initial_hds_dir_path = self.initial_hds_dir_path.resolve()
        exe_conf = ExecutionConfiguration(self.__default_environ_getter,
                                          self.__environ,
                                          self.__os_services,
                                          sandbox_root_name_resolver.for_test(),
                                          2 ** 10,
                                          SymbolTable())
        configuration_builder = ConfigurationBuilder(initial_hds_dir_path,
                                                     initial_hds_dir_path,
                                                     NameAndValue('the actor',
                                                                  self._actor()))
        full_result = execution.execute(
            exe_conf,
            configuration_builder,
            True,
            self._test_case())

        # ASSERT #
        self.__full_result = full_result
        self._assertions()
        # CLEANUP #
        os.chdir(str(self.initial_hds_dir_path))
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
    def initial_hds_dir_path(self) -> pathlib.Path:
        return self.__initial_hds_dir_path

    @property
    def full_result(self) -> FullExeResult:
        return self.__full_result

    @property
    def sds(self) -> SandboxDs:
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
