from typing import TypeVar, Generic

from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue, \
    SingleDirDependentValue
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.sym_ref_and_validation import ObjectWithSymbolReferencesAndValidation
from exactly_lib.util.symbol_table import SymbolTable

# Want to say that resolved values must be DirDependentValue,
# but do now know how to do this without listing multiple types - since TypeVar
# requires more than one type in the constraint.
DIR_DEP_TYPE = TypeVar('RESOLVED_TYPE', SingleDirDependentValue, MultiDirDependentValue)


class ResolverWithValidation(Generic[DIR_DEP_TYPE], ObjectWithSymbolReferencesAndValidation):
    @property
    def validator(self) -> PreOrPostSdsValidator:
        raise NotImplementedError('abstract method')

    def resolve_value(self, symbols: SymbolTable) -> DIR_DEP_TYPE:
        raise NotImplementedError('abstract method')
