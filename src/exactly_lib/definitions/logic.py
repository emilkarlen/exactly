from exactly_lib.util.logic_types import Quantifier
from .test_case import reserved_words

NOT_OPERATOR_NAME = reserved_words.NEGATION_OPERATOR

AND_OPERATOR_NAME = reserved_words.CONJUNCTION_OPERATOR

OR_OPERATOR_NAME = reserved_words.DISJUNCTION_OPERATOR

FALSE = 'false'
TRUE = 'true'

BOOLEANS = {
    False: FALSE,
    True: TRUE,
}

BOOLEANS_STRINGS = {
    item[1]: item[0]
    for item in BOOLEANS.items()
}

CONSTANT_MATCHER = 'constant'

ALL_QUANTIFIER_ARGUMENT = 'every'
EXISTS_QUANTIFIER_ARGUMENT = 'any'

QUANTIFICATION_SEPARATOR_ARGUMENT = reserved_words.COLON

QUANTIFIER_ARGUMENTS = {
    Quantifier.ALL: ALL_QUANTIFIER_ARGUMENT,
    Quantifier.EXISTS: EXISTS_QUANTIFIER_ARGUMENT,
}
