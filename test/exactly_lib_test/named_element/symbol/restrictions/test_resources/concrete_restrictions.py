from exactly_lib.named_element import resolver_structure as vs
from exactly_lib.named_element.symbol.restriction import ReferenceRestrictions, ValueRestriction, \
    ValueRestrictionFailure
from exactly_lib.named_element.symbol.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.named_element.symbol.restrictions.value_restrictions import NoRestriction


class RestrictionThatCannotBeSatisfied(ValueRestriction):
    def is_satisfied_by(self,
                        symbol_table: vs.SymbolTable,
                        symbol_name: str,
                        container: vs.ResolverContainer) -> ValueRestrictionFailure:
        return ValueRestrictionFailure('unconditional error')


def unconditionally_satisfied_reference_restrictions() -> ReferenceRestrictions:
    return ReferenceRestrictionsOnDirectAndIndirect(NoRestriction())


def unconditionally_unsatisfied_reference_restrictions() -> ReferenceRestrictions:
    return ReferenceRestrictionsOnDirectAndIndirect(RestrictionThatCannotBeSatisfied())
