import types
import unittest

from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds


class Expectation:
    def __init__(self,
                 passes_pre_sds: bool = True,
                 passes_post_sds: bool = True):
        self.passes_pre_sds = passes_pre_sds
        self.passes_post_sds = passes_post_sds


def expect_passes_all_validations() -> Expectation:
    return Expectation(True, True)


def expect_validation_pre_eds(result: bool) -> Expectation:
    return Expectation(result, True)


def check2(put: unittest.TestCase,
           validator: PreOrPostSdsValidator,
           environment: PathResolvingEnvironmentPreOrPostSds,
           expectation: Expectation):
    check(put, validator, environment,
          expectation.passes_pre_sds,
          expectation.passes_post_sds)


def check(put: unittest.TestCase,
          validator: PreOrPostSdsValidator,
          environment: PathResolvingEnvironmentPreOrPostSds,
          passes_pre_sds: bool = True,
          passes_post_sds: bool = True):
    def _check(f: types.FunctionType,
               message: str,
               expect_none: bool,
               arg):
        if expect_none:
            put.assertIsNone(f(arg),
                             message)
        else:
            put.assertIsNotNone(f(arg),
                                message)

    _check(validator.validate_pre_sds_if_applicable,
           'Validation pre SDS',
           passes_pre_sds,
           environment)
    _check(validator.validate_post_sds_if_applicable,
           'Validation post SDS',
           passes_post_sds,
           environment)
    _check(validator.validate_pre_or_post_sds,
           'Validation pre or post SDS',
           passes_pre_sds and passes_post_sds,
           environment)
