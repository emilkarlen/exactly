from exactly_lib.symbol import resolver_structure as vs
from exactly_lib.symbol.concrete_restrictions import ReferenceRestrictionsOnDirectAndIndirect, NoRestriction
from exactly_lib.symbol.value_restriction import ReferenceRestrictions, ValueRestriction, ValueRestrictionFailure


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
