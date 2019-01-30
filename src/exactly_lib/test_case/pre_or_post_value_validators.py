from typing import Optional, Sequence, Iterable

from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case.pre_or_post_value_validation import PreOrPostSdsValueValidator, constant_success_validator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.util.symbol_table import SymbolTable


class ValueValidatorFromResolverValidator(PreOrPostSdsValueValidator):
    def __init__(self,
                 symbols: SymbolTable,
                 adapted: PreOrPostSdsValidator):
        self._symbols = symbols
        self._adapted = adapted

    def validate_pre_sds_if_applicable(self, hds: HomeDirectoryStructure) -> Optional[str]:
        environment = PathResolvingEnvironmentPreSds(hds, self._symbols)
        return self._adapted.validate_pre_sds_if_applicable(environment)

    def validate_post_sds_if_applicable(self, tcds: HomeAndSds) -> Optional[str]:
        environment = PathResolvingEnvironmentPostSds(tcds.sds, self._symbols)
        return self._adapted.validate_post_sds_if_applicable(environment)


def all_of(validators: Sequence[PreOrPostSdsValueValidator]) -> PreOrPostSdsValueValidator:
    if len(validators) == 0:
        return constant_success_validator()
    elif len(validators) == 1:
        return validators[0]
    else:
        return AndValidator(validators)


class AndValidator(PreOrPostSdsValueValidator):
    def __init__(self,
                 validators: Iterable[PreOrPostSdsValueValidator]):
        self.validators = validators

    def validate_pre_sds_if_applicable(self, hds: HomeDirectoryStructure) -> Optional[str]:
        for validator in self.validators:
            result = validator.validate_pre_sds_if_applicable(hds)
            if result is not None:
                return result
        return None

    def validate_post_sds_if_applicable(self, tcds: HomeAndSds) -> Optional[str]:
        for validator in self.validators:
            result = validator.validate_post_sds_if_applicable(tcds)
            if result is not None:
                return result
        return None
