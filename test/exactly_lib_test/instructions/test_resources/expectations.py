from exactly_lib_test.instructions.test_resources.assertion_utils import svh_check
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


class ExpectationBase:
    def __init__(self,
                 validation_pre_sds: va.ValueAssertion = svh_check.is_success(),
                 main_side_effects_on_files: va.ValueAssertion = va.anything_goes(),
                 home_and_sds: va.ValueAssertion = va.anything_goes(),
                 ):
        self.validation_pre_sds = svh_check.is_svh_and(validation_pre_sds)
        self.main_side_effects_on_files = main_side_effects_on_files
        self.side_effects_check = home_and_sds
