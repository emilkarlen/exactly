import os
import shutil
import unittest

from exactly_lib.execution.configuration import ExecutionConfiguration
from exactly_lib.execution.partial_execution import execution as sut
from exactly_lib.execution.partial_execution.configuration import ConfPhaseValues, TestCase
from exactly_lib.execution.partial_execution.result import PartialExeResult
from exactly_lib.test_case import atc_os_proc_executors
from exactly_lib.test_case.actor import AtcOsProcessExecutor, Actor
from exactly_lib.test_case.phases import setup
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.file_utils.misc_utils import preserved_cwd
from exactly_lib_test.execution.test_resources import sandbox_root_name_resolver
from exactly_lib_test.test_case_file_structure.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from .basic import Result


class Arrangement:
    def __init__(self,
                 test_case: TestCase,
                 actor: Actor,
                 initial_setup_settings: setup.SetupSettingsBuilder = setup.default_settings(),
                 atc_os_process_executor: AtcOsProcessExecutor =
                 atc_os_proc_executors.DEFAULT_ATC_OS_PROCESS_EXECUTOR):
        self.test_case = test_case
        self.actor = actor
        self.initial_setup_settings = initial_setup_settings
        self.atc_os_process_executor = atc_os_process_executor


class Expectation:
    def __init__(self,
                 assertion_on_sds: ValueAssertion[SandboxDirectoryStructure] = asrt.anything_goes(),
                 phase_result: ValueAssertion[PartialExeResult] = asrt.anything_goes()):
        self.phase_result = phase_result
        self.assertion_on_sds = assertion_on_sds


def execute_and_check(put: unittest.TestCase,
                      arrangement: Arrangement,
                      expectation: Expectation):
    with home_directory_structure() as hds:
        with preserved_cwd():
            partial_result = sut.execute(
                arrangement.test_case,
                ExecutionConfiguration(dict(os.environ),
                                       arrangement.atc_os_process_executor,
                                       sandbox_root_name_resolver.for_test()),
                ConfPhaseValues(arrangement.actor,
                                hds),
                arrangement.initial_setup_settings,
                is_keep_sandbox=True)

            expectation.phase_result.apply_with_message(put,
                                                        partial_result,
                                                        'phase_result')
            result = Result(hds, partial_result)
            expectation.assertion_on_sds.apply_with_message(put,
                                                            result.partial_result.sds,
                                                            'Sandbox Directory Structure')
    # CLEANUP #
    if result is not None and result.sds is not None:
        if result.sds.root_dir.exists():
            shutil.rmtree(str(result.sds.root_dir))
