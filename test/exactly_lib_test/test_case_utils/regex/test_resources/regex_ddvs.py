from typing import Pattern, Sequence, Set, Optional

from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.ddv_validation import DdvValidator, \
    ConstantDdvValidator
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.regex.regex_ddv import RegexSdv, RegexDdv
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.symbol_table import SymbolTable


class RegexConstantDdvTestImpl(RegexDdv):
    def __init__(self,
                 value: Pattern[str],
                 resolving_dependencies: Optional[Set[DirectoryStructurePartition]] = None,
                 validator: DdvValidator = ConstantDdvValidator(None, None),
                 ):
        self._value = value
        self._validator = validator
        self._resolving_dependencies = set() if resolving_dependencies is None else resolving_dependencies

    def describer(self) -> DetailsRenderer:
        return custom_details.regex_with_config_renderer(False,
                                                         custom_details.PatternRenderer(self._value))

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._resolving_dependencies

    def value_when_no_dir_dependencies(self) -> Pattern:
        return self._value

    def value_of_any_dependency(self, tcds: Tcds) -> Pattern:
        return self._value

    def validator(self) -> DdvValidator:
        return self._validator


class RegexSdvConstantTestImpl(RegexSdv):
    def __init__(self,
                 resolved_value: Pattern[str],
                 references: Sequence[SymbolReference] = (),
                 resolving_dependencies: Optional[Set[DirectoryStructurePartition]] = None,
                 value_validator: DdvValidator = ConstantDdvValidator(None, None)):
        self._references = list(references)
        self._resolving_dependencies = resolving_dependencies
        self._value_validator = value_validator
        self._resolved_value = resolved_value

    @property
    def resolved_value(self) -> Pattern:
        return self._resolved_value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> RegexDdv:
        return RegexConstantDdvTestImpl(self._resolved_value,
                                        self._resolving_dependencies,
                                        self._value_validator)