import unittest
from typing import Callable

from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds, \
    PathResolvingEnvironmentPreSds, PathResolvingEnvironmentPostSds, PathResolvingEnvironment
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib_test.test_resources.actions import do_nothing


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


def check(put: unittest.TestCase,
          validator: PreOrPostSdsValidator,
          environment: PathResolvingEnvironmentPreOrPostSds,
          expectation: Expectation):
    def _check(f: Callable[[PathResolvingEnvironment], str],
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
           expectation.passes_pre_sds,
           environment)
    _check(validator.validate_post_sds_if_applicable,
           'Validation post SDS',
           expectation.passes_post_sds,
           environment)
    _check(validator.validate_pre_or_post_sds,
           'Validation pre or post SDS',
           expectation.passes_pre_sds and expectation.passes_post_sds,
           environment)


class ValidatorThat(PreOrPostSdsValidator):
    def __init__(self,
                 pre_sds_action=do_nothing,
                 pre_sds_return_value=None,
                 post_setup_action=do_nothing,
                 post_setup_return_value=None,
                 ):
        self.post_setup_return_value = post_setup_return_value
        self.pre_sds_return_value = pre_sds_return_value
        self.post_setup_action = post_setup_action
        self.pre_sds_action = pre_sds_action

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> str:
        self.pre_sds_action(environment)
        return self.pre_sds_return_value

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> str:
        self.post_setup_action(environment)
        return self.post_setup_return_value
