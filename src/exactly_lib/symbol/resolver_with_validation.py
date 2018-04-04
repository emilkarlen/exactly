from typing import Generic

from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.symbol.utils import DIR_DEP_TYPE, DirDepValueResolver
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.util.symbol_table import SymbolTable


class WithValidation:
    @property
    def validator(self) -> PreOrPostSdsValidator:
        raise NotImplementedError('abstract method')


class ObjectWithSymbolReferencesAndValidation(ObjectWithTypedSymbolReferences, WithValidation):
    pass


class DirDepValueResolverWithValidation(Generic[DIR_DEP_TYPE], DirDepValueResolver[DIR_DEP_TYPE], WithValidation):
    @property
    def validator(self) -> PreOrPostSdsValidator:
        raise NotImplementedError('abstract method')

    def resolve(self, symbols: SymbolTable) -> DIR_DEP_TYPE:
        raise NotImplementedError('abstract method')
