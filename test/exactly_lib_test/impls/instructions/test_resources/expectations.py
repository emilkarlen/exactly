from exactly_lib_test.test_case.result.test_resources import svh_assertions
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


class ExpectationBase:
    def __init__(self,
                 validation_pre_sds: Assertion,
                 main_side_effects_on_sds: Assertion,
                 main_side_effects_on_tcds: Assertion,
                 symbol_usages: Assertion,
                 ):
        self.validation_pre_sds = svh_assertions.is_svh_and(validation_pre_sds)
        self.main_side_effects_on_sds = main_side_effects_on_sds
        self.main_side_effects_on_tcds = main_side_effects_on_tcds
        self.symbol_usages = symbol_usages
