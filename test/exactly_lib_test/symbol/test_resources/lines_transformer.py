from exactly_lib.symbol.resolver_structure import LinesTransformerResolver
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import resolver_structure_assertions as asrt_ne
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class LinesTransformerResolverConstantTestImpl(LinesTransformerResolver):
    def __init__(self, resolved_value: LinesTransformer,
                 references: list = ()):
        self._resolved_value = resolved_value
        self._references = list(references)

    @property
    def resolved_value(self) -> LinesTransformer:
        return self._resolved_value

    @property
    def references(self) -> list:
        return self._references

    def resolve(self, named_elements: SymbolTable) -> LinesTransformer:
        return self._resolved_value


IS_LINES_TRANSFORMER_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.LINES_TRANSFORMER)


def is_lines_transformer_reference_to(name_of_transformer: str) -> asrt.ValueAssertion:
    return asrt_ne.matches_reference(asrt.equals(name_of_transformer),
                                     IS_LINES_TRANSFORMER_REFERENCE_RESTRICTION)
