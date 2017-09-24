from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.resolver_structure import LinesTransformerResolver, LineMatcherResolver
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.lines_transformer import transformers
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class LinesTransformerConstant(LinesTransformerResolver):
    """
    A :class:`LinesTransformerResolver` that is a constant :class:`LinesTransformer`
    """

    def __init__(self, value: LinesTransformer):
        self._value = value

    def resolve(self, symbols: SymbolTable) -> LinesTransformer:
        return self._value

    @property
    def references(self) -> list:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._value) + '\''


class LinesTransformerReference(LinesTransformerResolver):
    """
    A :class:`LinesTransformerResolver` that is a reference to a symbol
    """

    def __init__(self, name_of_referenced_resolver: str):
        self._name_of_referenced_resolver = name_of_referenced_resolver
        self._references = [SymbolReference(name_of_referenced_resolver,
                                            ValueTypeRestriction(ValueType.LINES_TRANSFORMER))]

    def resolve(self, symbols: SymbolTable) -> LinesTransformer:
        container = symbols.lookup(self._name_of_referenced_resolver)
        resolver = container.resolver
        assert isinstance(resolver, LinesTransformerResolver)
        return resolver.resolve(symbols)

    @property
    def references(self) -> list:
        return self._references

    def __str__(self):
        return str(type(self)) + '\'' + str(self._name_of_referenced_resolver) + '\''


class LinesTransformerSelectResolver(LinesTransformerResolver):
    """
    Resolver of :class:`SelectLinesTransformer`
    """

    def __init__(self, line_matcher_resolver: LineMatcherResolver):
        self.line_matcher_resolver = line_matcher_resolver

    def resolve(self, symbols: SymbolTable) -> LinesTransformer:
        return transformers.SelectLinesTransformer(self.line_matcher_resolver.resolve(symbols))

    @property
    def references(self) -> list:
        return self.line_matcher_resolver.references


class LinesTransformerSequenceResolver(LinesTransformerResolver):
    """
    Resolver of :class:`LinesTransformerSequence`
    """

    def __init__(self, transformer_resolver_list: list):
        self.transformers = transformer_resolver_list
        self._references = references_from_objects_with_symbol_references(transformer_resolver_list)

    def resolve(self, symbols: SymbolTable) -> LinesTransformer:
        return transformers.SequenceLinesTransformer([
            transformer.resolve(symbols)
            for transformer in self.transformers
        ])

    @property
    def references(self) -> list:
        return self._references
