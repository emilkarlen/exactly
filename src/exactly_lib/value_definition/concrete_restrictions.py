from exactly_lib.test_case_file_structure.file_ref_relativity import PathRelativityVariants
from exactly_lib.test_case_file_structure.relativity_validation import is_satisfied_by
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.value_definition.concrete_values import FileRefValue
from exactly_lib.value_definition.value_structure import ValueRestriction, Value


class NoRestriction(ValueRestriction):
    """
    No restriction - a restriction that any value satisfies.
    """

    def is_satisfied_by(self, symbol_table: SymbolTable, value: Value) -> str:
        return None


class FileRefRelativityRestriction(ValueRestriction):
    """
    Restricts to `FileRefValue` and `PathRelativityVariants`
    """

    def __init__(self, accepted: PathRelativityVariants):
        self._accepted = accepted

    def is_satisfied_by(self, symbol_table: SymbolTable, value: Value) -> str:
        if not isinstance(value, FileRefValue):
            #  TODO [val-def] Error message should be human readable
            return 'Not a FileRefValue: ' + str(value)
        file_ref = value.file_ref
        actual_relativity = file_ref.specific_relativity(symbol_table)
        return is_satisfied_by(actual_relativity, self._accepted)

    @property
    def accepted(self) -> PathRelativityVariants:
        return self._accepted
