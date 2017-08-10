from enum import Enum

from exactly_lib.instructions.assert_.utils.negation_of_assertion import NEGATION_ARGUMENT_STR
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class ExpectationType(Enum):
    POSITIVE = 0
    NEGATIVE = 1


def with_negation_argument(instruction_arguments: str) -> str:
    return NEGATION_ARGUMENT_STR + ' ' + instruction_arguments


class NotOperatorInfo:
    def __init__(self, is_negated: bool):
        self.is_negated = is_negated

    @property
    def nothing__if_un_negated_else__not_option(self) -> str:
        return NEGATION_ARGUMENT_STR if self.is_negated else ''

    @property
    def pass__if_un_negated_else__fail(self) -> asrt.ValueAssertion:
        return pfh_check.is_fail() if self.is_negated else pfh_check.is_pass()

    @property
    def fail__if_un_negated_else__pass(self) -> asrt.ValueAssertion:
        return pfh_check.is_pass() if self.is_negated else pfh_check.is_fail()
