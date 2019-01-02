from typing import Pattern, Sequence, Set, Optional

from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case import pre_or_post_validation
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.regex.regex_value import RegexResolver, RegexValue
from exactly_lib.util.symbol_table import SymbolTable


class RegexConstantValueTestImpl(RegexValue):
    def __init__(self,
                 value: Pattern,
                 resolving_dependencies: Optional[Set[DirectoryStructurePartition]] = None
                 ):
        self._value = value
        self._resolving_dependencies = set() if resolving_dependencies is None else resolving_dependencies

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._resolving_dependencies

    def value_when_no_dir_dependencies(self) -> Pattern:
        return self._value

    def value_of_any_dependency(self, tcds: HomeAndSds) -> Pattern:
        return self._value


class RegexResolverConstantTestImpl(RegexResolver):
    def __init__(self,
                 resolved_value: Pattern,
                 references: Sequence[SymbolReference] = (),
                 resolving_dependencies: Optional[Set[DirectoryStructurePartition]] = None,
                 validator: PreOrPostSdsValidator = pre_or_post_validation.ConstantSuccessValidator()):
        self._references = list(references)
        self._resolving_dependencies = resolving_dependencies
        self._validator = validator
        self._resolved_value = resolved_value

    @property
    def resolved_value(self) -> Pattern:
        return self._resolved_value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def resolve(self, symbols: SymbolTable) -> RegexValue:
        return RegexConstantValueTestImpl(self._resolved_value,
                                          self._resolving_dependencies)
