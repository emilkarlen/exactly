import unittest

from shellcheck_lib.test_case.sections.anonymous import ConfigurationBuilder


class Assertion:
    def apply(self,
              put: unittest.TestCase,
              initial: ConfigurationBuilder,
              actual_result: ConfigurationBuilder):
        raise NotImplementedError()


class AnythingGoes(Assertion):
    def apply(self,
              put: unittest.TestCase,
              initial: ConfigurationBuilder,
              actual_result: ConfigurationBuilder):
        pass


class UnconditionalFail(Assertion):
    def apply(self,
              put: unittest.TestCase,
              initial: ConfigurationBuilder,
              actual_result: ConfigurationBuilder):
        put.fail('Unconditional')
