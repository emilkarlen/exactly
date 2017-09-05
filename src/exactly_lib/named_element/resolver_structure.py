from exactly_lib.named_element.object_with_symbol_references import ObjectWithSymbolReferences
from exactly_lib.named_element.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer
from exactly_lib.type_system.value_type import SymbolValueType, ValueType, ElementType, LogicValueType
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import SymbolTableValue, SymbolTable


class NamedElementResolver(ObjectWithSymbolReferences):
    """ Base class for values in the symbol table used by Exactly. """

    @property
    def element_type(self) -> ElementType:
        raise NotImplementedError('abstract method')

    @property
    def value_type(self) -> ValueType:
        raise NotImplementedError('abstract method')

    @property
    def references(self) -> list:
        """
        All :class:`NamedElementReference` directly referenced by this object.

        :type: [`SymbolReference`]
        """
        raise NotImplementedError('abstract method')


def get_references(resolver: NamedElementResolver) -> list:
    return resolver.references


def get_element_type(resolver: NamedElementResolver) -> ElementType:
    return resolver.element_type


def get_value_type(resolver: NamedElementResolver) -> ValueType:
    return resolver.value_type


class LogicValueResolver(NamedElementResolver):
    """ Base class for logic values - values that represent functionality/logic."""

    @property
    def element_type(self) -> ElementType:
        return ElementType.LOGIC

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


class SymbolValueResolver(NamedElementResolver):
    """ Base class for symbol values - values that represent data."""

    @property
    def element_type(self) -> ElementType:
        return ElementType.SYMBOL

    @property
    def data_value_type(self) -> SymbolValueType:
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


def get_data_value_type(resolver: SymbolValueResolver) -> SymbolValueType:
    return resolver.data_value_type


class NamedElementContainer(SymbolTableValue):
    """
    The info about a named element resolver that is stored in a symbol table.

    A value together with meta info
    """

    def __init__(self,
                 value_resolver: NamedElementResolver,
                 source: Line):
        self._source = source
        self._resolver = value_resolver
        self._source = source

    @property
    def definition_source(self) -> Line:
        """
        The source code of the definition of the value.

        :rtype None iff the symbol is built in.
        """
        return self._source

    @property
    def resolver(self) -> NamedElementResolver:
        return self._resolver


def container_of_builtin(value_resolver: NamedElementResolver) -> NamedElementContainer:
    return NamedElementContainer(value_resolver, None)
