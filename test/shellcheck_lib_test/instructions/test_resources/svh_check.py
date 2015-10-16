import unittest

from shellcheck_lib.test_case.sections.result import svh


class Assertion:
    def apply(self,
              put: unittest.TestCase,
              actual: svh.SuccessOrValidationErrorOrHardError):
        raise NotImplementedError()


class StatusIs(Assertion):
    def __init__(self,
                 expected_status: svh.SuccessOrValidationErrorOrHardErrorEnum):
        self.expected_status = expected_status

    def apply(self,
              put: unittest.TestCase,
              actual: svh.SuccessOrValidationErrorOrHardError):
        put.assertIs(self.expected_status,
                     actual.status,
                     'Status')


def is_success():
    return StatusIs(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS)


def is_hard_error():
    return StatusIs(svh.SuccessOrValidationErrorOrHardErrorEnum.HARD_ERROR)


def is_validation_error():
    return StatusIs(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR)


class AnythingGoes(Assertion):
    def apply(self,
              put: unittest.TestCase,
              actual: svh.SuccessOrValidationErrorOrHardError):
        pass


class NotApplicable(Assertion):
    def apply(self,
              put: unittest.TestCase,
              actual: svh.SuccessOrValidationErrorOrHardError):
        put.fail('Not applicable')
