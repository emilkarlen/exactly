from typing import Sequence

from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.name_and_value import NameAndValue


def symbol_ref_syntax_cases(symbol_name: str) -> Sequence[NameAndValue[str]]:
    return [
        NameAndValue('plain',
                     symbol_name,
                     ),
        NameAndValue('reference syntax',
                     symbol_reference_syntax_for_name(symbol_name),
                     ),
    ]
