from enum import Enum

from exactly_lib.instructions.assert_.utils.negation_of_assertion import NEGATION_ARGUMENT_STR


class CheckType(Enum):
    POSITIVE = 0
    NEGATIVE = 1


def with_negation_argument(instruction_arguments: str) -> str:
    return NEGATION_ARGUMENT_STR + ' ' + instruction_arguments
