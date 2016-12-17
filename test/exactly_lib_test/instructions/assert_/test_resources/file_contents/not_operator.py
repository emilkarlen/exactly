from exactly_lib.instructions.assert_.utils.file_contents import parsing
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


class NotOperatorInfo:
    def __init__(self, is_negated: bool):
        self.is_negated = is_negated

    def nothing__if_un_negated_else__not_option(self) -> str:  # TODO make to prop
        return parsing.NOT_ARGUMENT if self.is_negated else ''

    def pass__if_un_negated_else__fail(self) -> va.ValueAssertion:
        return pfh_check.is_fail() if self.is_negated else pfh_check.is_pass()

    def fail__if_un_negated_else__pass(self) -> va.ValueAssertion:
        return pfh_check.is_pass() if self.is_negated else pfh_check.is_fail()
