import unittest

from shellcheck_lib.test_case.sections import common

from shellcheck_lib.test_case.sections.setup import SetupSettingsBuilder


class Assertion:
    def apply(self,
              put: unittest.TestCase,
              environment: common.GlobalEnvironmentForPostEdsPhase,
              initial: SetupSettingsBuilder,
              actual_result: SetupSettingsBuilder):
        raise NotImplementedError()


class AnythingGoes(Assertion):
    def apply(self,
              put: unittest.TestCase,
              environment: common.GlobalEnvironmentForPostEdsPhase,
              initial: SetupSettingsBuilder,
              actual_result: SetupSettingsBuilder):
        pass


class UnconditionalFail(Assertion):
    def apply(self,
              put: unittest.TestCase,
              environment: common.GlobalEnvironmentForPostEdsPhase,
              initial: SetupSettingsBuilder,
              actual_result: SetupSettingsBuilder):
        put.fail('Unconditional')
