import types
import unittest

from shellcheck_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsValidator
from shellcheck_lib.test_case.sections.common import HomeAndEds


def check(put: unittest.TestCase,
          validator: PreOrPostEdsValidator,
          home_and_eds: HomeAndEds,
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
           'Validation pre EDS',
           passes_pre_eds,
           home_and_eds.home_dir_path)
    _check(validator.validate_post_eds_if_applicable,
           'Validation post EDS',
           passes_post_eds,
           home_and_eds.eds)
    _check(validator.validate_pre_or_post_eds,
           'Validation pre or post EDS',
           passes_pre_eds and passes_post_eds,
           home_and_eds)
