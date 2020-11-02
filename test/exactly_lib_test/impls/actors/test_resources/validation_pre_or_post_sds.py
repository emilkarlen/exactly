from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib_test.impls.types.test_resources import validation
from exactly_lib_test.impls.types.test_resources.validation import ValidationExpectationSvh


class ValidationCase:
    def __init__(self,
                 name: str,
                 path_relativity: RelOptionType,
                 expectation: ValidationExpectationSvh,
                 ):
        self.name = name
        self.path_relativity = path_relativity
        self.expectation = expectation


VALIDATION_CASES = [
    ValidationCase(
        'pre sds',
        RelOptionType.REL_HDS_CASE,
        validation.pre_sds_validation_fails__svh(),
    ),
    ValidationCase(
        'post sds',
        RelOptionType.REL_ACT,
        validation.post_sds_validation_hard_error__svh(),
    ),
]
