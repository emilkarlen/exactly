import types

from exactly_lib.execution.error_message_format import defined_at_line__err_msg_lines
from exactly_lib.named_element.resolver_structure import NamedElementContainer, SymbolValueResolver
from exactly_lib.named_element.restriction import FailureInfo, \
    SymbolReferenceRestrictions
from exactly_lib.named_element.symbol.restrictions.value_restrictions import NoRestriction, StringRestriction
from exactly_lib.named_element.symbol.value_restriction import ValueRestrictionFailure, ValueRestriction
from exactly_lib.type_system_values.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class FailureOfDirectReference(FailureInfo):
    def __init__(self, error: ValueRestrictionFailure):
        self._error = error

    @property
    def error(self) -> ValueRestrictionFailure:
        return self._error


class FailureOfIndirectReference(FailureInfo):
    def __init__(self,
                 failing_symbol: str,
                 path_to_failing_symbol: list,
                 error: ValueRestrictionFailure,
                 meaning_of_failure: str = ''):
        self._failing_symbol = failing_symbol
        self._path_to_failing_symbol = path_to_failing_symbol
        self._error = error
        self._meaning_of_failure = meaning_of_failure

    @property
    def failing_symbol(self) -> str:
        """
        The name of the symbol that causes the failure
        """
        return self._failing_symbol

    @property
    def path_to_failing_symbol(self) -> list:
        """
        The references (from top to bottom) that leads to the failing symbol
        """
        return self._path_to_failing_symbol

    @property
    def error(self) -> ValueRestrictionFailure:
        return self._error

    @property
    def meaning_of_failure(self) -> str:
        return self._meaning_of_failure


class ReferenceRestrictionsOnDirectAndIndirect(SymbolReferenceRestrictions):
    """
    Restriction with one `ValueRestriction` that is applied on the
    directly referenced symbol; and another that (if it is not None) is applied on every indirectly
    referenced symbol.
    """

    def __init__(self,
                 direct: ValueRestriction,
                 indirect: ValueRestriction = None,
                 meaning_of_failure_of_indirect_reference: str = ''):
        self._direct = direct
        self._indirect = indirect
        self._meaning_of_failure_of_indirect_reference = meaning_of_failure_of_indirect_reference

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: NamedElementContainer) -> FailureInfo:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param value: The value that the restriction applies to
        :return: None if satisfied, otherwise an error message
        """
        result = self._direct.is_satisfied_by(symbol_table, symbol_name, container)
        if result is not None:
            return FailureOfDirectReference(result)
        if self._indirect is None:
            return None
        return self.check_indirect(symbol_table, container.resolver.references)

    @property
    def direct(self) -> ValueRestriction:
        """
        Restriction on the symbol that is the direct target of the reference.
        """
        return self._direct

    @property
    def indirect(self) -> ValueRestriction:
        """
        Restriction that must be satisfied by the symbols references indirectly referenced.
        :rtype: None or ValueRestriction
        """
        return self._indirect

    @property
    def meaning_of_failure_of_indirect_reference(self) -> str:
        return self._meaning_of_failure_of_indirect_reference

    def check_indirect(self,
                       symbol_table: SymbolTable,
                       references: list) -> FailureOfIndirectReference:
        return self._check_indirect(symbol_table, (), references)

    def _check_indirect(self,
                        symbol_table: SymbolTable,
                        path_to_referring_symbol: tuple,
                        references: list) -> FailureOfIndirectReference:
        for reference in references:
            container = symbol_table.lookup(reference.name)
            result = self._indirect.is_satisfied_by(symbol_table, reference.name, container)
            if result is not None:
                return FailureOfIndirectReference(
                    failing_symbol=reference.name,
                    path_to_failing_symbol=list(path_to_referring_symbol),
                    error=result,
                    meaning_of_failure=self._meaning_of_failure_of_indirect_reference)
            result = self._check_indirect(symbol_table,
                                          path_to_referring_symbol + (reference.name,),
                                          container.resolver.references)
            if result is not None:
                return result
        return None


class OrRestrictionPart(tuple):
    def __new__(cls,
                selector: ValueType,
                restriction: ReferenceRestrictionsOnDirectAndIndirect):
        return tuple.__new__(cls, (selector, restriction))

    @property
    def selector(self) -> ValueType:
        return self[0]

    @property
    def restriction(self) -> ReferenceRestrictionsOnDirectAndIndirect:
        return self[1]


class OrReferenceRestrictions(SymbolReferenceRestrictions):
    def __init__(self,
                 or_restriction_parts: list,
                 resolver_container_2_error_message_if_no_matching_part: types.FunctionType = None):
        self._parts = tuple(or_restriction_parts)
        self._container_2_error_message_if_no_matching_part = resolver_container_2_error_message_if_no_matching_part

    @property
    def parts(self) -> tuple:
        return self._parts

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: NamedElementContainer) -> FailureInfo:
        resolver = container.resolver
        assert isinstance(resolver, SymbolValueResolver)  # Type info for IDE
        for part in self._parts:
            assert isinstance(part, OrRestrictionPart)  # Type info for IDE
            if part.selector == resolver.value_type:
                return part.restriction.is_satisfied_by(symbol_table, symbol_name, container)
        return self._no_satisfied_restriction(symbol_name, resolver, container)

    def _no_satisfied_restriction(self,
                                  symbol_name: str,
                                  resolver: SymbolValueResolver,
                                  value: NamedElementContainer) -> FailureOfDirectReference:
        if self._container_2_error_message_if_no_matching_part is not None:
            msg = self._container_2_error_message_if_no_matching_part(value)
        else:
            msg = self._default_error_message(symbol_name, value, resolver)
        return FailureOfDirectReference(ValueRestrictionFailure(msg))

    def _default_error_message(self,
                               symbol_name: str,
                               container: NamedElementContainer,
                               resolver: SymbolValueResolver) -> str:
        from exactly_lib.help_texts.test_case.instructions import assign_symbol
        accepted_value_types = ', '.join([assign_symbol.TYPE_INFO_DICT[part.selector].type_name
                                          for part in self._parts])
        lines = ([
                     'Invalid type, of symbol "{}"'.format(symbol_name)
                 ] +
                 defined_at_line__err_msg_lines(container.definition_source) +
                 [
                     '',
                     'Accepted : ' + accepted_value_types,
                     'Found    : ' + assign_symbol.TYPE_INFO_DICT[resolver.value_type].type_name,
                 ])
        return '\n'.join(lines)


class SymbolReferenceRestrictionsVisitor:
    def visit(self, x: SymbolReferenceRestrictions):
        if isinstance(x, ReferenceRestrictionsOnDirectAndIndirect):
            return self.visit_direct_and_indirect(x)
        if isinstance(x, OrReferenceRestrictions):
            return self.visit_or(x)
        raise TypeError('%s is not an instance of %s' % (str(x), str(SymbolReferenceRestrictions)))

    def visit_direct_and_indirect(self, x: ReferenceRestrictionsOnDirectAndIndirect):
        raise NotImplementedError()

    def visit_or(self, x: OrReferenceRestrictions):
        raise NotImplementedError()


def no_restrictions() -> SymbolReferenceRestrictions:
    """
    :return: A restriction that is unconditionally satisfied
    """
    return ReferenceRestrictionsOnDirectAndIndirect(NoRestriction())


def string_made_up_by_just_strings(meaning_of_failure_of_indirect_reference: str = ''
                                   ) -> ReferenceRestrictionsOnDirectAndIndirect:
    return ReferenceRestrictionsOnDirectAndIndirect(
        direct=StringRestriction(),
        indirect=StringRestriction(),
        meaning_of_failure_of_indirect_reference=meaning_of_failure_of_indirect_reference)
