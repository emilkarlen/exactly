import unittest

from shellcheck_lib.test_case.instruction.result import svh
from shellcheck_lib.test_case.instruction.result import pfh


class Assertion:
    def apply(self,
              put: unittest.TestCase,
              actual: pfh.PassOrFailOrHardError):
        raise NotImplementedError()


class StatusIs(Assertion):
    def __init__(self,
                 expected_status: pfh.PassOrFailOrHardErrorEnum):
        self.expected_status = expected_status

    def apply(self,
              put: unittest.TestCase,
              actual: pfh.PassOrFailOrHardError):
        put.assertIs(self.expected_status,
                     actual.status,
                     'Status')


def is_pass():
    return StatusIs(pfh.PassOrFailOrHardErrorEnum.PASS)


def is_fail():
    return StatusIs(pfh.PassOrFailOrHardErrorEnum.FAIL)


class AnythingGoes(Assertion):
    def apply(self,
              put: unittest.TestCase,
              actual: pfh.PassOrFailOrHardError):
        pass


class NotApplicable(Assertion):
    def apply(self,
              put: unittest.TestCase,
              actual: svh.SuccessOrValidationErrorOrHardError):
        put.fail('Not applicable')
