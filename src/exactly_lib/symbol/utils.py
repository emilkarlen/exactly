from typing import TypeVar, Generic

from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.test_case_file_structure.dir_dependent_value import SingleDirDependentValue, MultiDirDependentValue
from exactly_lib.util.symbol_table import SymbolTable

RESOLVED_TYPE = TypeVar('RESOLVED_TYPE')

DIR_DEP_TYPE = TypeVar('DIR_DEP_TYPE', SingleDirDependentValue, MultiDirDependentValue)


class ValueResolver(Generic[RESOLVED_TYPE], ObjectWithTypedSymbolReferences):
    def resolve(self, symbols: SymbolTable) -> RESOLVED_TYPE:
        raise NotImplementedError('abstract method')


class DirDepValueResolver(Generic[DIR_DEP_TYPE], ValueResolver[DIR_DEP_TYPE]):
    def resolve(self, symbols: SymbolTable) -> DIR_DEP_TYPE:
        raise NotImplementedError('abstract method')
