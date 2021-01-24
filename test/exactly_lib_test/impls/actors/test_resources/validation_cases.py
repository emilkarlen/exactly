from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib_test.impls.test_resources.validation.svh_validation import ValidationExpectationSvh


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
        ValidationExpectationSvh.fails__pre_sds(),
    ),
    ValidationCase(
        'post sds',
        RelOptionType.REL_ACT,
        ValidationExpectationSvh.hard_error__post_sds(),
    ),
]
