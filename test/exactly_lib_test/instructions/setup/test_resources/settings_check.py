import unittest

from exactly_lib.test_case.phases import common
from exactly_lib.test_case.phases.setup import SetupSettingsBuilder


class Model(tuple):
    def __new__(cls,
                actual: SetupSettingsBuilder,
                environment: common.InstructionEnvironmentForPostSdsStep,
                ):
        return tuple.__new__(cls, (actual, environment))

    @property
    def actual(self) -> SetupSettingsBuilder:
        return self[0]

    @property
    def environment(self) -> common.InstructionEnvironmentForPostSdsStep:
        return self[1]


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
