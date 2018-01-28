from exactly_lib.symbol.object_with_symbol_references import ObjectWithSymbolReferences
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer
from exactly_lib.type_system.value_type import DataValueType, ValueType, TypeCategory, LogicValueType
from exactly_lib.util.line_source import LineSequence
from exactly_lib.util.symbol_table import SymbolTableValue, SymbolTable


class SymbolValueResolver(ObjectWithSymbolReferences):
    """ Base class for values in the symbol table used by Exactly. """

    @property
    def type_category(self) -> TypeCategory:
        raise NotImplementedError('abstract method')

    @property
    def value_type(self) -> ValueType:
        raise NotImplementedError('abstract method')

    @property
    def references(self) -> list:
        """
        All :class:`SymbolReference` directly referenced by this object.

        :type: [`SymbolReference`]
        """
        raise NotImplementedError('abstract method')


def get_references(resolver: SymbolValueResolver) -> list:
    return resolver.references


def get_type_category(resolver: SymbolValueResolver) -> TypeCategory:
    return resolver.type_category


def get_value_type(resolver: SymbolValueResolver) -> ValueType:
    return resolver.value_type


class LogicValueResolver(SymbolValueResolver):
    """ Base class for logic values - values that represent functionality/logic."""

    @property
    def type_category(self) -> TypeCategory:
        return TypeCategory.LOGIC

    @property
    def logic_value_type(self) -> LogicValueType:
        raise NotImplementedError('abstract method')


def get_logic_value_type(resolver: LogicValueResolver) -> LogicValueType:
    return resolver.logic_value_type


class FileMatcherResolver(LogicValueResolver):
    """ Base class for resolvers of :class:`FileMatcher`. """

    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.FILE_MATCHER

    @property
    def value_type(self) -> ValueType:
        return ValueType.FILE_MATCHER

    @property
    def references(self) -> list:
        raise NotImplementedError('abstract method')

    def resolve(self, named_elements: SymbolTable) -> FileMatcher:
        raise NotImplementedError('abstract method')


class LineMatcherResolver(LogicValueResolver):
    """ Base class for resolvers of :class:`LineMatcher`. """

    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.LINE_MATCHER

    @property
    def value_type(self) -> ValueType:
        return ValueType.LINE_MATCHER

    @property
    def references(self) -> list:
        raise NotImplementedError('abstract method')

    def resolve(self, symbols: SymbolTable) -> LineMatcher:
        raise NotImplementedError('abstract method')


class LinesTransformerResolver(LogicValueResolver):
    """ Base class for resolvers of :class:`LinesTransformer`. """

    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.LINES_TRANSFORMER

    @property
    def value_type(self) -> ValueType:
        return ValueType.LINES_TRANSFORMER

    @property
    def references(self) -> list:
        raise NotImplementedError('abstract method')

    def resolve(self, named_elements: SymbolTable) -> LinesTransformer:
        raise NotImplementedError('abstract method')


class DataValueResolver(SymbolValueResolver):
    """ Base class for symbol values - values that represent data."""

    @property
    def type_category(self) -> TypeCategory:
        return TypeCategory.DATA

    @property
    def data_value_type(self) -> DataValueType:
        raise NotImplementedError('abstract method')

    @property
    def value_type(self) -> ValueType:
        raise NotImplementedError('abstract method')

    @property
    def references(self) -> list:
        raise NotImplementedError('abstract method')

    def resolve(self, symbols: SymbolTable) -> DirDependentValue:
        """
        Resolves the value given a symbol table.
        :rtype: Depends on the concrete value.
        """
        raise NotImplementedError('abstract method')

    def resolve_value_of_any_dependency(self, environment: PathResolvingEnvironmentPreOrPostSds):
        """
        Short cut for resolving the value_of_any_dependency
        """
        return self.resolve(environment.symbols).value_of_any_dependency(environment.home_and_sds)


def get_data_value_type(resolver: DataValueResolver) -> DataValueType:
    return resolver.data_value_type


class SymbolContainer(SymbolTableValue):
    """
    The info about a named element resolver that is stored in a symbol table.

    A value together with meta info
    """

    def __init__(self,
                 value_resolver: SymbolValueResolver,
                 source: LineSequence):
        self._resolver = value_resolver
        self._source = source

    @property
    def definition_source(self) -> LineSequence:
        """
        The source code of the definition of the value.

        :rtype None iff the symbol is built in.
        """
        return self._source

    @property
    def resolver(self) -> SymbolValueResolver:
        return self._resolver


def container_of_builtin(value_resolver: SymbolValueResolver) -> SymbolContainer:
    return SymbolContainer(value_resolver, None)
