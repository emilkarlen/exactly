import unittest

from shellcheck_lib.test_case.instruction.sections.setup import SetupSettingsBuilder


class Assertion:
    def apply(self,
              put: unittest.TestCase,
              initial: SetupSettingsBuilder,
              actual_result: SetupSettingsBuilder):
        raise NotImplementedError()


class AnythingGoes(Assertion):
    def apply(self,
              put: unittest.TestCase,
              initial: SetupSettingsBuilder,
              actual_result: SetupSettingsBuilder):
        pass


class UnconditionalFail(Assertion):
    def apply(self,
              put: unittest.TestCase,
              initial: SetupSettingsBuilder,
              actual_result: SetupSettingsBuilder):
        pass
