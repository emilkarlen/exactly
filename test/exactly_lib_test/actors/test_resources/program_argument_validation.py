from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib_test.actors.test_resources.integration_check import Expectation
from exactly_lib_test.test_case_utils.test_resources import validation


class ValidationCase:
    def __init__(self,
                 name: str,
                 path_relativity: RelOptionType,
                 expectation: Expectation,
                 ):
        self.name = name
        self.path_relativity = path_relativity
        self.expectation = expectation


ARGUMENT_VALIDATION_CASES = [
    ValidationCase(
        'pre sds',
        RelOptionType.REL_HDS_CASE,
        Expectation(validation=validation.pre_sds_validation_fails__svh()),
    ),
    ValidationCase(
        'post sds',
        RelOptionType.REL_ACT,
        Expectation(validation=validation.post_sds_validation_hard_error__svh()),
    ),
]
