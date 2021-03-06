import shutil
import unittest
from typing import Optional

from exactly_lib.execution.configuration import ExecutionConfiguration
from exactly_lib.execution.partial_execution import execution as sut
from exactly_lib.execution.partial_execution.configuration import ConfPhaseValues, TestCase
from exactly_lib.execution.partial_execution.execution import MkSetupSettingsHandler
from exactly_lib.execution.partial_execution.result import PartialExeResult
from exactly_lib.execution.predefined_properties import os_environ_getter
from exactly_lib.impls.os_services import os_services_access
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.act.actor import Actor
from exactly_lib.util.file_utils.misc_utils import preserved_cwd
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.execution.test_resources import sandbox_root_name_resolver
from exactly_lib_test.tcfs.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from . import settings_handlers
from .basic import Result


class Arrangement:
    def __init__(self,
                 test_case: TestCase,
                 actor: Actor,
                 settings_handler: Optional[MkSetupSettingsHandler] = None,
                 os_services: OsServices = os_services_access.new_for_current_os(),
                 mem_buff_size: int = 2 ** 10,
                 timeout_in_seconds: Optional[int] = None,
                 ):
        self.test_case = test_case
        self.actor = actor
        self.timeout_in_seconds = timeout_in_seconds
        self.settings_handler = settings_handlers.mk_from_optional(settings_handler)
        self.os_services = os_services
        self.mem_buff_size = mem_buff_size


class Expectation:
    def __init__(self,
                 assertion_on_sds: Assertion[SandboxDs] = asrt.anything_goes(),
                 phase_result: Assertion[PartialExeResult] = asrt.anything_goes()):
        self.phase_result = phase_result
        self.assertion_on_sds = assertion_on_sds


def execute_and_check(put: unittest.TestCase,
                      arrangement: Arrangement,
                      expectation: Expectation):
    with home_directory_structure() as hds:
        with preserved_cwd():
            partial_result = sut.execute(
                arrangement.test_case,
                ExecutionConfiguration(os_environ_getter,
                                       None,
                                       arrangement.timeout_in_seconds,
                                       arrangement.os_services,
                                       sandbox_root_name_resolver.for_test(),
                                       arrangement.mem_buff_size),
                ConfPhaseValues(NameAndValue('the actor', arrangement.actor),
                                hds),
                arrangement.settings_handler,
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
