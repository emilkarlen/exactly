from exactly_lib_test.test_case_utils.test_resources import svh_assertions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class ExpectationBase:
    def __init__(self,
                 validation_pre_sds: asrt.ValueAssertion,
                 main_side_effects_on_sds: asrt.ValueAssertion,
                 main_side_effects_on_home_and_sds: asrt.ValueAssertion,
                 symbol_usages: asrt.ValueAssertion,
                 ):
        self.validation_pre_sds = svh_assertions.is_svh_and(validation_pre_sds)
        self.main_side_effects_on_sds = main_side_effects_on_sds
        self.main_side_effects_on_home_and_sds = main_side_effects_on_home_and_sds
        self.symbol_usages = symbol_usages
