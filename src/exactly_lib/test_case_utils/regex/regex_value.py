from typing import Sequence, Set, Pattern

from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.util.symbol_table import SymbolTable


class RegexValue(MultiDirDependentValue[Pattern]):
    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        raise NotImplementedError('abstract method')

    def validator(self) -> PreOrPostSdsValueValidator:
        raise NotImplementedError('abstract method')

    def value_when_no_dir_dependencies(self) -> Pattern:
        raise NotImplementedError('abstract method')

    def value_of_any_dependency(self, tcds: HomeAndSds) -> Pattern:
        raise NotImplementedError('abstract method')


class RegexResolver:
    """ Base class for resolvers of :class:`StringMatcherValue`. """

    @property
    def references(self) -> Sequence[SymbolReference]:
        raise NotImplementedError('abstract method')

    def resolve(self, symbols: SymbolTable) -> RegexValue:
        raise NotImplementedError('abstract method')
