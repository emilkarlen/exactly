import unittest

from exactly_lib.test_case.phases import common
from exactly_lib.test_case.phases.setup import SetupSettingsBuilder


class Assertion:
    def apply(self,
              put: unittest.TestCase,
              environment: common.InstructionEnvironmentForPostSdsStep,
              initial: SetupSettingsBuilder,
              actual_result: SetupSettingsBuilder):
        raise NotImplementedError()


class AnythingGoes(Assertion):
    def apply(self,
              put: unittest.TestCase,
              environment: common.InstructionEnvironmentForPostSdsStep,
              initial: SetupSettingsBuilder,
              actual_result: SetupSettingsBuilder):
        pass


class UnconditionalFail(Assertion):
    def apply(self,
              put: unittest.TestCase,
              environment: common.InstructionEnvironmentForPostSdsStep,
              initial: SetupSettingsBuilder,
              actual_result: SetupSettingsBuilder):
        put.fail('Unconditional')
