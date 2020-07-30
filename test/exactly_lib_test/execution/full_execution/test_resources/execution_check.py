import os
import unittest

from exactly_lib.execution.configuration import PredefinedProperties, ExecutionConfiguration
from exactly_lib.execution.full_execution import execution
from exactly_lib.execution.full_execution.result import FullExeResult
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.test_case.phases.setup import SetupSettingsBuilder
from exactly_lib.test_case_utils.os_services import os_services_access
from exactly_lib_test.execution.test_resources import sandbox_root_name_resolver
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class Arrangement:
    def __init__(self,
                 test_case: test_case_doc.TestCase,
                 configuration_builder: ConfigurationBuilder,
                 initial_settings_builder: SetupSettingsBuilder = None,
                 predefined_properties: PredefinedProperties = PredefinedProperties({}),
                 os_services: OsServices = os_services_access.new_for_current_os(),

                 ):
        self.test_case = test_case
        self.predefined_properties = predefined_properties
        self.configuration_builder = configuration_builder
        if not initial_settings_builder:
            initial_settings_builder = SetupSettingsBuilder()
        self.initial_settings_builder = initial_settings_builder
        self.os_services = os_services


class Expectation:
    def __init__(self,
                 full_result: ValueAssertion[FullExeResult] = asrt.anything_goes()):
        self.full_result = full_result


def check(put: unittest.TestCase,
          arrangement: Arrangement,
          expectation: Expectation,
          is_keep_sandbox: bool = False):
    exe_conf = ExecutionConfiguration(dict(os.environ),
                                      arrangement.os_services,
                                      sandbox_root_name_resolver.for_test(),
                                      arrangement.predefined_properties.predefined_symbols)
    result = execution.execute(
        exe_conf,
        arrangement.configuration_builder,
        is_keep_sandbox,
        arrangement.test_case)
    expectation.full_result.apply(put, result, asrt.MessageBuilder('FullExeResult'))
