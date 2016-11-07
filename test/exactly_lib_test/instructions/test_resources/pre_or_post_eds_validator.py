import types
import unittest

from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsValidator
from exactly_lib.test_case.phases.common import HomeAndSds


def check(put: unittest.TestCase,
          validator: PreOrPostEdsValidator,
          home_and_sds: HomeAndSds,
          passes_pre_eds: bool = True,
          passes_post_eds: bool = True):
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

    _check(validator.validate_pre_eds_if_applicable,
           'Validation pre SDS',
           passes_pre_eds,
           home_and_sds.home_dir_path)
    _check(validator.validate_post_eds_if_applicable,
           'Validation post SDS',
           passes_post_eds,
           home_and_sds.sds)
    _check(validator.validate_pre_or_post_eds,
           'Validation pre or post SDS',
           passes_pre_eds and passes_post_eds,
           home_and_sds)
