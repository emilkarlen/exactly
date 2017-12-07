from exactly_lib.help_texts import type_system
from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.symbol.data.restrictions import error_messages
from exactly_lib.symbol.data.value_restriction import ValueRestrictionFailure, ValueRestriction
from exactly_lib.symbol.err_msg import error_messages as err_msg_for_any_type
from exactly_lib.symbol.resolver_structure import SymbolContainer
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants
from exactly_lib.test_case_file_structure.relativity_validation import is_satisfied_by
from exactly_lib.type_system.value_type import ValueType, TypeCategory
from exactly_lib.util.symbol_table import SymbolTable


class AnyDataTypeRestriction(ValueRestriction):
    """
    A restriction that any data symbol value satisfies.
    """

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: SymbolContainer) -> ValueRestrictionFailure:
        if container.resolver.type_category is not TypeCategory.DATA:
            return err_msg_for_any_type.invalid_type_msg(
                [type_system.DATA_TYPE_2_VALUE_TYPE[symbol_type]
                 for symbol_type in type_system.DATA_TYPE_LIST_ORDER],
                symbol_name,
                container)
        return None


class StringRestriction(ValueRestriction):
    """
    Restriction to string values.
    """

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: SymbolContainer) -> ValueRestrictionFailure:
        if container.resolver.value_type is not ValueType.STRING:
            return err_msg_for_any_type.invalid_type_msg([ValueType.STRING], symbol_name, container)
        return None


class FileRefRelativityRestriction(ValueRestriction):
    """
    Restricts to `FileRefValue` and `PathRelativityVariants`
    """

    def __init__(self, accepted: PathRelativityVariants):
        self._accepted = accepted

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: SymbolContainer) -> ValueRestrictionFailure:
        resolver = container.resolver
        if not isinstance(resolver, FileRefResolver):
            return err_msg_for_any_type.invalid_type_msg([ValueType.PATH], symbol_name, container)
        file_ref = resolver.resolve(symbol_table)
        actual_relativity = file_ref.relativity()
        satisfaction = is_satisfied_by(actual_relativity, self._accepted)
        if satisfaction:
            return None
        else:
            msg = error_messages.unsatisfied_path_relativity(symbol_name, container,
                                                             self._accepted,
                                                             actual_relativity)
            return ValueRestrictionFailure(msg)

    @property
    def accepted(self) -> PathRelativityVariants:
        return self._accepted


class ValueRestrictionVisitor:
    def visit(self, x: ValueRestriction):
        if isinstance(x, AnyDataTypeRestriction):
            return self.visit_none(x)
        if isinstance(x, StringRestriction):
            return self.visit_string(x)
        if isinstance(x, FileRefRelativityRestriction):
            return self.visit_file_ref_relativity(x)
        raise TypeError('%s is not an instance of %s' % (str(x), str(ValueRestriction)))

    def visit_none(self, x: AnyDataTypeRestriction):
        raise NotImplementedError()

    def visit_string(self, x: StringRestriction):
        raise NotImplementedError()

    def visit_file_ref_relativity(self, x: FileRefRelativityRestriction):
        raise NotImplementedError()
