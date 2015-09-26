import unittest

from shellcheck_lib.test_case.instruction.result import sh


class Assertion:
    def apply(self,
              put: unittest.TestCase,
              actual: sh.SuccessOrHardError):
        raise NotImplementedError()


class IsSuccess(Assertion):
    def apply(self,
              put: unittest.TestCase,
              actual: sh.SuccessOrHardError):
        put.assertTrue(actual.is_success,
                       'Status is expected to be success (was {})'.format(actual))


class IsHardError(Assertion):
    def apply(self,
              put: unittest.TestCase,
              actual: sh.SuccessOrHardError):
        put.assertTrue(actual.is_hard_error,
                       'Status is expected to be hard-error (was {})'.format(actual))


class AnythingGoes(Assertion):
    def apply(self,
              put: unittest.TestCase,
              actual: sh.SuccessOrHardError):
        pass


class NotApplicable(Assertion):
    def apply(self,
              put: unittest.TestCase,
              actual: sh.SuccessOrHardError):
        put.fail('Not applicable')
