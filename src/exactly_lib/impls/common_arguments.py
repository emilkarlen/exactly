from exactly_lib.definitions.test_case import reserved_words
from exactly_lib.util.cli_syntax.elements import argument as a

RESERVED_WORD__COLON = a.Single(a.Multiplicity.MANDATORY, a.Constant(reserved_words.COLON))
