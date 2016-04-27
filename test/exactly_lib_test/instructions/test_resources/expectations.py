from exactly_lib_test.instructions.test_resources import svh_check__va
from exactly_lib_test.test_resources import value_assertion as va


class ExpectationBase:
    def __init__(self,
                 validation_pre_eds: va.ValueAssertion = svh_check__va.is_success(),
                 main_side_effects_on_files: va.ValueAssertion = va.anything_goes(),
                 home_and_eds: va.ValueAssertion = va.anything_goes(),
                 ):
        self.validation_pre_eds = svh_check__va.is_svh_and(validation_pre_eds)
        self.main_side_effects_on_files = main_side_effects_on_files
        self.side_effects_check = home_and_eds
