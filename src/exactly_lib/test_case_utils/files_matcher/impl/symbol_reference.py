from typing import Sequence

from exactly_lib.symbol import lookups
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironment
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.pre_or_post_validation import ValidatorOfReferredResolverBase, \
    PreOrPostSdsValidator
from exactly_lib.type_system.logic.files_matcher import FilesMatcherDdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


def symbol_reference_matcher(name_of_referenced_sdv: str) -> FilesMatcherSdv:
    return _ReferenceSdv(name_of_referenced_sdv)


class _ReferenceSdv(FilesMatcherSdv):
    def __init__(self, name_of_referenced_sdv: str):
        self._name_of_referenced_sdv = name_of_referenced_sdv
        self._references = [SymbolReference(name_of_referenced_sdv,
                                            ValueTypeRestriction(ValueType.FILES_MATCHER))]
        self._validator = _ValidatorOfReferredResolver(name_of_referenced_sdv)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def resolve(self, symbols: SymbolTable) -> FilesMatcherDdv:
        sdv = lookups.lookup_files_matcher(symbols, self._name_of_referenced_sdv)
        return sdv.resolve(symbols)

    def __str__(self):
        return str(type(self)) + '\'' + str(self._name_of_referenced_sdv) + '\''


class _ValidatorOfReferredResolver(ValidatorOfReferredResolverBase):
    def _referred_validator(self, environment: PathResolvingEnvironment) -> PreOrPostSdsValidator:
        referred_matcher_sdv = lookups.lookup_files_matcher(environment.symbols, self.symbol_name)
        return referred_matcher_sdv.validator()
