from enum import Enum

from exactly_lib.instructions.assert_.utils.negation_of_assertion import NEGATION_ARGUMENT_STR
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class ExpectationType(Enum):
    """
    Tells if an boolean expression is expected to be
    True (POSITIVE) or False (NEGATIVE)
    """
    POSITIVE = 0
    NEGATIVE = 1


def with_negation_argument(instruction_arguments: str) -> str:
    return NEGATION_ARGUMENT_STR + ' ' + instruction_arguments


class ExpectationTypeConfig:
    def __init__(self, expectation_type: ExpectationType):
        if not isinstance(expectation_type, ExpectationType):
            raise ValueError('not exp_ty')
        self._expectation_type = expectation_type

    @property
    def expectation_type(self) -> ExpectationType:
        return self._expectation_type

    @property
    def expectation_type_str(self) -> str:
        return str(self._expectation_type)

    def __str__(self) -> str:
        return 'expectation_type=' + self.expectation_type_str

    @property
    def nothing__if_positive__not_option__if_negative(self) -> str:
        return self._value('', NEGATION_ARGUMENT_STR)

    @property
    def pass__if_positive__fail__if_negative(self) -> asrt.ValueAssertion:
        return self._value(pfh_check.is_pass(),
                           pfh_check.is_fail())

    @property
    def fail__if_positive__pass_if_negative(self) -> asrt.ValueAssertion:
        return self._value(pfh_check.is_fail(),
                           pfh_check.is_pass())

    def _value(self,
               value_for_positive,
               value_for_negative):
        return value_for_positive if self.expectation_type is ExpectationType.POSITIVE else value_for_negative


def expectation_type_conf_from_is_negated(is_negated: bool) -> ExpectationTypeConfig:
    expectation_type = ExpectationType.NEGATIVE if is_negated else ExpectationType.POSITIVE
    return ExpectationTypeConfig(expectation_type)
