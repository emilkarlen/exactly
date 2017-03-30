from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants
from exactly_lib.test_case_file_structure.relativity_validation import is_satisfied_by
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.value_definition.concrete_values import FileRefValue, StringValue
from exactly_lib.value_definition.value_structure import ValueRestriction, Value


class NoRestriction(ValueRestriction):
    """
    No restriction - a restriction that any value satisfies.
    """

    def is_satisfied_by(self, symbol_table: SymbolTable, value: Value) -> str:
        return None


class StringRestriction(ValueRestriction):
    """
    Restriction to string values.
    """

    def is_satisfied_by(self, symbol_table: SymbolTable, value: Value) -> str:
        if not isinstance(value, StringValue):
            #  TODO [val-def] Error message should be human readable
            return 'Not a StringValueValue: ' + str(value)
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


class ValueRestrictionVisitor:
    def visit(self, x: ValueRestriction):
        if isinstance(x, NoRestriction):
            return self.visit_none(x)
        if isinstance(x, StringRestriction):
            return self.visit_string(x)
        if isinstance(x, FileRefRelativityRestriction):
            return self.visit_file_ref_relativity(x)
        raise TypeError('%s is not an instance of %s' % (str(x), str(ValueRestriction)))

    def visit_none(self, x: NoRestriction):
        raise NotImplementedError()

    def visit_string(self, x: StringRestriction):
        raise NotImplementedError()

    def visit_file_ref_relativity(self, x: FileRefRelativityRestriction):
        raise NotImplementedError()
