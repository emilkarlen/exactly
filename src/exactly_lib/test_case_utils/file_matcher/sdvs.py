from typing import Sequence, Callable

from exactly_lib.symbol import lookups
from exactly_lib.symbol.logic.file_matcher import FileMatcherSdv
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.file_matcher import file_matcher_ddvs as ddvs
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherDdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class FileMatcherConstantSdv(FileMatcherSdv):
    """
    A :class:`FileMatcherSdv` that is a constant :class:`FileMatcher`
    """

    def __init__(self, value: FileMatcher):
        self._value = value

    def resolve(self, symbols: SymbolTable) -> FileMatcherDdv:
        return ddvs.FileMatcherValueFromPrimitiveDdv(self._value)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._value) + '\''


class FileMatcherReferenceSdv(FileMatcherSdv):
    """
    A :class:`FileMatcherSdv` that is a reference to a symbol
    """

    def __init__(self, name_of_referenced_sdv: str):
        self._name_of_referenced_sdv = name_of_referenced_sdv
        self._references = [SymbolReference(name_of_referenced_sdv,
                                            ValueTypeRestriction(ValueType.FILE_MATCHER))]

    def resolve(self, symbols: SymbolTable) -> FileMatcherDdv:
        sdv = lookups.lookup_file_matcher(symbols, self._name_of_referenced_sdv)
        return sdv.resolve(symbols)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def __str__(self):
        return str(type(self)) + '\'' + str(self._name_of_referenced_sdv) + '\''


class FileMatcherNotSdv(FileMatcherSdv):
    def __init__(self, file_matcher_sdv: FileMatcherSdv):
        self._sdv = file_matcher_sdv

    def resolve(self, symbols: SymbolTable) -> FileMatcherDdv:
        return ddvs.FileMatcherNotValue(self._sdv.resolve(symbols))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._sdv.references


class FileMatcherAndSdv(FileMatcherSdv):
    def __init__(self, parts: Sequence[FileMatcherSdv]):
        self._resolvers = parts
        self._references = references_from_objects_with_symbol_references(parts)

    def resolve(self, symbols: SymbolTable) -> FileMatcherDdv:
        return ddvs.FileMatcherAndValue([
            part.resolve(symbols)
            for part in self._resolvers
        ])

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references


class FileMatcherOrSdv(FileMatcherSdv):
    def __init__(self, parts: Sequence[FileMatcherSdv]):
        self._resolvers = parts
        self._references = references_from_objects_with_symbol_references(parts)

    def resolve(self, symbols: SymbolTable) -> FileMatcherDdv:
        return ddvs.FileMatcherOrValue([
            part.resolve(symbols)
            for part in self._resolvers
        ])

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references


class FileMatcherSdvFromParts(FileMatcherSdv):
    def __init__(self,
                 references: Sequence[SymbolReference],
                 validator: DdvValidator,
                 matcher: Callable[[PathResolvingEnvironmentPreOrPostSds], FileMatcher]):
        self._matcher = matcher
        self._validator = validator
        self._references = references

    def resolve(self, symbols: SymbolTable) -> FileMatcherDdv:
        def get_matcher(tcds: Tcds) -> FileMatcher:
            environment = PathResolvingEnvironmentPreOrPostSds(tcds, symbols)
            return self._matcher(environment)

        return ddvs.FileMatcherDdvFromParts(self._validator,
                                            get_matcher,
                                            )

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def __str__(self):
        return str(type(self))


class FileMatcherSdvFromValueParts(FileMatcherSdv):
    def __init__(self,
                 references: Sequence[SymbolReference],
                 make_ddv: Callable[[SymbolTable], FileMatcherDdv]):
        self._make_value = make_ddv
        self._references = references

    def resolve(self, symbols: SymbolTable) -> FileMatcherDdv:
        return self._make_value(symbols)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def __str__(self):
        return str(type(self))
