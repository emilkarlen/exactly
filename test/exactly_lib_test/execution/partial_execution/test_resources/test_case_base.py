import os
import pathlib
import shutil
import unittest

import exactly_lib.act_phase_setups.source_interpreter.python3
from exactly_lib import program_info
from exactly_lib.execution import partial_execution
from exactly_lib.execution.partial_execution import TestCase
from exactly_lib.execution.result import PartialResult
from exactly_lib.processing.processors import act_phase_handling_for_setup
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib.test_case.os_services import ACT_PHASE_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phases import setup
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.file_utils import preserved_cwd
from exactly_lib_test.execution.test_resources import utils
from exactly_lib_test.test_case_file_structure.test_resources.hds_utils import home_directory_structure


class PartialExecutionTestCaseBase:
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False,
                 act_phase_handling: ActPhaseHandling = None):
        self.__put = unittest_case
        self.__dbg_do_not_delete_dir_structure = dbg_do_not_delete_dir_structure
        self.__partial_result = None
        self.__sandbox_directory_structure = None
        self.__act_phase_handling = act_phase_handling
        if self.__act_phase_handling is None:
            self.__act_phase_handling = act_phase_handling_for_setup(
                exactly_lib.act_phase_setups.source_interpreter.python3.new_act_phase_setup())

    def execute(self):
        # SETUP #
        with preserved_cwd():
            with home_directory_structure() as hds:
                # ACT #
                partial_result = partial_execution.execute(
                    self.__act_phase_handling,
                    self._test_case(),
                    partial_execution.Configuration(ACT_PHASE_OS_PROCESS_EXECUTOR,
                                                    hds,
                                                    dict(os.environ)),
                    setup.default_settings(),
                    program_info.PROGRAM_NAME + '-test-',
                    self.__dbg_do_not_delete_dir_structure)

                # ASSERT #
                self.__partial_result = partial_result
                self._assertions()
        # CLEANUP #
        if not self.__dbg_do_not_delete_dir_structure and self.sds:
            if self.sds.root_dir.exists():
                shutil.rmtree(str(self.sds.root_dir))
        else:
            if self.sds:
                print(str(self.sds.root_dir))

    def _test_case(self) -> TestCase:
        raise NotImplementedError()

    def _assertions(self):
        raise NotImplementedError()

    @property
    def put(self) -> unittest.TestCase:
        return self.__put

    @property
    def partial_result(self) -> PartialResult:
        return self.__partial_result

    @property
    def sds(self) -> SandboxDirectoryStructure:
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
