import pathlib
import shutil
import unittest

from exactly_lib.execution.configuration import ExecutionConfiguration
from exactly_lib.execution.partial_execution import execution as sut
from exactly_lib.execution.partial_execution.configuration import ConfPhaseValues
from exactly_lib.execution.partial_execution.configuration import TestCase
from exactly_lib.execution.partial_execution.result import PartialExeResult
from exactly_lib.execution.partial_execution.setup_settings_handler import StandardSetupSettingsHandler
from exactly_lib.execution.predefined_properties import os_environ_getter
from exactly_lib.impls.os_services import os_services_access
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.test_case.phases.act.actor import Actor
from exactly_lib.test_case.phases.environ import OptionalEnvVarsDict
from exactly_lib.test_case.phases.setup.settings_handler import SetupSettingsHandler
from exactly_lib.util.file_utils.misc_utils import preserved_cwd
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.execution.test_resources import utils, sandbox_root_name_resolver
from exactly_lib_test.impls.actors.test_resources import python3
from exactly_lib_test.tcfs.test_resources.hds_utils import home_directory_structure


class PartialExecutionTestCaseBase:
    def __init__(self,
                 put: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False,
                 actor: Actor = None):
        self.__put = put
        self.__dbg_do_not_delete_dir_structure = dbg_do_not_delete_dir_structure
        self.__partial_result = None
        self.__sandbox_directory_structure = None
        self.__actor = actor
        if self.__actor is None:
            self.__actor = python3.new_actor()

    def execute(self):
        # SETUP #
        with preserved_cwd():
            with home_directory_structure() as hds:
                # ACT #
                partial_result = sut.execute(
                    self._test_case(),
                    ExecutionConfiguration(os_environ_getter,
                                           None,
                                           os_services_access.new_for_current_os(),
                                           sandbox_root_name_resolver.for_test(),
                                           2 ** 10),
                    ConfPhaseValues(NameAndValue('the actor', self.__actor),
                                    hds),
                    self._mk_settings_handler,
                    self.__dbg_do_not_delete_dir_structure)

                # ASSERT #
                self.__partial_result = partial_result
                self._assertions()
        # CLEANUP #
        if not self.__dbg_do_not_delete_dir_structure and self.sds:
            if self.sds.root_dir.exists():
                shutil.rmtree(str(self.sds.root_dir),
                              ignore_errors=True)
        else:
            if self.sds:
                print(str(self.sds.root_dir))

    def _test_case(self) -> TestCase:
        raise NotImplementedError()

    def _mk_settings_handler(self, environ: OptionalEnvVarsDict) -> SetupSettingsHandler:
        return StandardSetupSettingsHandler.new_from_environ(environ)

    def _assertions(self):
        raise NotImplementedError()

    @property
    def put(self) -> unittest.TestCase:
        return self.__put

    @property
    def partial_result(self) -> PartialExeResult:
        return self.__partial_result

    @property
    def sds(self) -> SandboxDs:
        return self.__partial_result.sds

    def assert_is_regular_file_with_contents(self,
                                             path: pathlib.Path,
                                             expected_contents: str,
                                             msg=None):
        """
        Helper for test cases that check the contents of files.
        """
        utils.assert_is_file_with_contents(self.put,
                                           path,
                                           expected_contents,
                                           msg)
