from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions


class Symbol:
    def __init__(self,
                 name: str,
                 value_int: int,
                 value_str: str,
                 ):
        self.name = name
        self.value_int = value_int
        self.value_str = value_str
        self.ref_syntax = symbol_reference_syntax_for_name(name)
        self.symbol_reference = SymbolReference(
            name,
            reference_restrictions.is_string__all_indirect_refs_are_strings()
        )


class Expected:
    def __init__(self,
                 resolved_value: int,
                 symbol_references: Sequence[SymbolReference],
                 ):
        self.resolved_value = resolved_value
        self.symbol_references = symbol_references


class Case:
    def __init__(self,
                 name: str,
                 source: str,
                 expected: Expected,
                 ):
        self.name = name
        self.source = source
        self.expected = expected
