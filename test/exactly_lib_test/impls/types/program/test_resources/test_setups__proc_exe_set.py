import unittest
from abc import ABC, abstractmethod
from typing import Dict

from exactly_lib.impls.os_services import os_services_access
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_case.test_resources.command_executors import CommandExecutorThatChecksProcExeSettings
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes import \
    ProgramOfSystemCommandLineAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import StringLiteralAbsStx
from exactly_lib_test.util.process_execution.test_resources import proc_exe_env_assertions as asrt_pe


class TestSetupBase(ABC):
    def __init__(self,
                 put: unittest.TestCase,
                 expectation: Assertion[ProcessExecutionSettings],
                 exit_code: int = 0,
                 ):
        self.exit_code = exit_code
        self.command_executor_w_check = CommandExecutorThatChecksProcExeSettings(
            put,
            expectation,
            exit_code,
        )

    @property
    def os_services__w_settings_check(self) -> OsServices:
        return os_services_access.new_for_cmd_exe(self.command_executor_w_check)

    @property
    def proc_exe_arr__w_settings_check(self) -> ProcessExecutionArrangement:
        return ProcessExecutionArrangement(
            self.os_services__w_settings_check,
            self._proc_exe_settings_w_expected_value(),
        )

    @staticmethod
    def valid_program_wo_sym_refs() -> ProgramAbsStx:
        return ProgramOfSystemCommandLineAbsStx(
            StringLiteralAbsStx('system-command'),
        )

    @abstractmethod
    def _proc_exe_settings_w_expected_value(self) -> ProcessExecutionSettings:
        pass


class TimeoutTestSetup(TestSetupBase):
    def __init__(self,
                 put: unittest.TestCase,
                 expected_timeout: int,
                 exit_code: int = 0,
                 ):
        super().__init__(
            put,
            asrt_pe.matches(
                timeout_in_seconds=asrt.equals(expected_timeout),
            ),
            exit_code,
        )
        self.expected_timeout = expected_timeout

    def _proc_exe_settings_w_expected_value(self) -> ProcessExecutionSettings:
        return ProcessExecutionSettings.with_timeout(self.expected_timeout)


class EnvironTestSetup(TestSetupBase):
    def __init__(self,
                 put: unittest.TestCase,
                 expected_environ: Dict[str, str],
                 exit_code: int = 0,
                 ):
        super().__init__(
            put,
            asrt_pe.matches(
                environ=asrt.equals(expected_environ),
            ),
            exit_code,
        )
        self.expected_environ = expected_environ

    def _proc_exe_settings_w_expected_value(self) -> ProcessExecutionSettings:
        return ProcessExecutionSettings.with_environ(self.expected_environ)
