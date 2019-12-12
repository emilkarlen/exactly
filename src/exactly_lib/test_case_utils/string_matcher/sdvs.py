from typing import Sequence, Callable

from exactly_lib.symbol import lookups
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.string_matcher import delegated_matcher
from exactly_lib.test_case_utils.string_matcher import string_matchers
from exactly_lib.type_system.logic import string_matcher_ddvs
from exactly_lib.type_system.logic.impls import combinator_matchers
from exactly_lib.type_system.logic.string_matcher import StringMatcher, StringMatcherDdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable


def new_with_transformation(transformer: StringTransformerSdv,
                            original: StringMatcherSdv) -> StringMatcherSdv:
    return _StringMatcherSvdWithTransformation(transformer, original)


def new_reference(name_of_referenced_sdv: str,
                  expectation_type: ExpectationType) -> StringMatcherSdv:
    return StringMatcherSdvReference(name_of_referenced_sdv, expectation_type)


class StringMatcherSvdConstant(StringMatcherSdv):
    """
    A :class:`StringMatcherResolver` that is a constant :class:`StringMatcher`
    """

    def __init__(self, value: StringMatcher):
        self._value = string_matcher_ddvs.StringMatcherConstantDdv(value)

    def resolve(self, symbols: SymbolTable) -> StringMatcherDdv:
        return self._value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._value) + '\''


class StringMatcherSdvConstantOfDdv(StringMatcherSdv):
    """
    A :class:`StringMatcherResolver` that is a constant :class:`StringMatcherValue`
    """

    def __init__(self, value: StringMatcherDdv):
        self._value = value

    def resolve(self, symbols: SymbolTable) -> StringMatcherDdv:
        return self._value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._value) + '\''


class _StringMatcherSvdWithTransformation(StringMatcherSdv):
    """
    A :class:`StringMatcherResolver` that transforms the model with a :class:`StringTransformerResolver`
    """

    def __init__(self,
                 transformer: StringTransformerSdv,
                 original: StringMatcherSdv,
                 ):
        self._transformer = transformer
        self._original = original

    def resolve(self, symbols: SymbolTable) -> StringMatcherDdv:
        return string_matchers.StringMatcherWithTransformationDdv(
            self._transformer.resolve(symbols),
            self._original.resolve(symbols),
        )

    @property
    def references(self) -> Sequence[SymbolReference]:
        return list(self._transformer.references) + list(self._original.references)

    def __str__(self):
        return str(type(self))


class StringMatcherSdvFromParts2(StringMatcherSdv):
    def __init__(self,
                 references: Sequence[SymbolReference],
                 get_ddv: Callable[[SymbolTable], StringMatcherDdv],
                 ):
        self._get_ddv = get_ddv
        self._references = references

    def resolve(self, symbols: SymbolTable) -> StringMatcherDdv:
        return self._get_ddv(symbols)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def __str__(self):
        return str(type(self))


class StringMatcherSdvReference(StringMatcherSdv):
    """
    A :class:`StringMatcherResolver` that is a reference to a symbol
    """

    def __init__(self,
                 name_of_referenced_sdv: str,
                 expectation_type: ExpectationType):
        self._name_of_referenced_sdv = name_of_referenced_sdv
        self._references = [SymbolReference(name_of_referenced_sdv,
                                            ValueTypeRestriction(ValueType.STRING_MATCHER))]
        self._expectation_type = expectation_type

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> StringMatcherDdv:
        sdv = lookups.lookup_string_matcher(symbols,
                                            self._name_of_referenced_sdv)
        referenced_value = sdv.resolve(symbols)

        if self._expectation_type is ExpectationType.POSITIVE:
            return referenced_value
        else:
            return self._negated(referenced_value)

    @staticmethod
    def _negated(original: StringMatcherDdv) -> StringMatcherDdv:
        return delegated_matcher.StringMatcherDdvDelegatedToMatcher(
            combinator_matchers.NegationDdv(original)
        )

    def __str__(self):
        return str(type(self)) + '\'' + str(self._name_of_referenced_sdv) + '\''
