from typing import Optional

from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case.pre_or_post_value_validation import PreOrPostSdsValueValidator
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
