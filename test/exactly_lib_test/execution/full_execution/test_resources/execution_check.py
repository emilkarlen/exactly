import unittest

from exactly_lib import program_info
from exactly_lib.execution import full_execution
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.test_case.phases.setup import SetupSettingsBuilder
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


class Arrangement:
    def __init__(self,
                 test_case: test_case_doc.TestCase,
                 configuration_builder: ConfigurationBuilder,
                 initial_settings_builder: SetupSettingsBuilder = None):
        self.test_case = test_case
        self.configuration_builder = configuration_builder
        if not initial_settings_builder:
            initial_settings_builder = SetupSettingsBuilder()
        self.initial_settings_builder = initial_settings_builder


class Expectation:
    def __init__(self,
                 full_result: va.ValueAssertion = va.anything_goes()):
        self.full_result = full_result


def check(put: unittest.TestCase,
          arrangement: Arrangement,
          expectation: Expectation,
          is_keep_execution_directory_root: bool = False):
    result = full_execution.execute(arrangement.test_case,
                                    arrangement.configuration_builder,
                                    program_info.PROGRAM_NAME + '-full-execution',
                                    is_keep_execution_directory_root)
    expectation.full_result.apply(put, result, va.MessageBuilder('FullResult'))
