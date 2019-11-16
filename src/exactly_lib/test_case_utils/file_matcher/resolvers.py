from typing import Sequence, Callable

from exactly_lib.symbol import lookups
from exactly_lib.symbol.logic.file_matcher import FileMatcherResolver
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.file_matcher import file_matcher_ddvs as ddvs
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherDdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class FileMatcherConstantResolver(FileMatcherResolver):
    """
    A :class:`FileMatcherResolver` that is a constant :class:`FileMatcher`
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


class FileMatcherReferenceResolver(FileMatcherResolver):
    """
    A :class:`FileMatcherResolver` that is a reference to a symbol
    """

    def __init__(self, name_of_referenced_resolver: str):
        self._name_of_referenced_resolver = name_of_referenced_resolver
        self._references = [SymbolReference(name_of_referenced_resolver,
                                            ValueTypeRestriction(ValueType.FILE_MATCHER))]

    def resolve(self, symbols: SymbolTable) -> FileMatcherDdv:
        resolver = lookups.lookup_file_matcher(symbols, self._name_of_referenced_resolver)
        return resolver.resolve(symbols)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def __str__(self):
        return str(type(self)) + '\'' + str(self._name_of_referenced_resolver) + '\''


class FileMatcherNotResolver(FileMatcherResolver):
    def __init__(self, file_matcher_resolver: FileMatcherResolver):
        self._resolver = file_matcher_resolver

    def resolve(self, symbols: SymbolTable) -> FileMatcherDdv:
        return ddvs.FileMatcherNotValue(self._resolver.resolve(symbols))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._resolver.references


class FileMatcherAndResolver(FileMatcherResolver):
    def __init__(self, parts: Sequence[FileMatcherResolver]):
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


class FileMatcherOrResolver(FileMatcherResolver):
    def __init__(self, parts: Sequence[FileMatcherResolver]):
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


class FileMatcherResolverFromParts(FileMatcherResolver):
    def __init__(self,
                 references: Sequence[SymbolReference],
                 validator: PreOrPostSdsValueValidator,
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


class FileMatcherResolverFromValueParts(FileMatcherResolver):
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
