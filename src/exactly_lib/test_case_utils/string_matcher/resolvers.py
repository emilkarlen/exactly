from typing import Sequence, Callable

from exactly_lib.symbol import lookups
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.symbol.logic.string_transformer import StringTransformerResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironment
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import pre_or_post_validation
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.string_matcher import delegated_matcher
from exactly_lib.test_case_utils.string_matcher import string_matchers
from exactly_lib.type_system.logic import string_matcher_ddvs
from exactly_lib.type_system.logic.impls import combinator_matchers
from exactly_lib.type_system.logic.string_matcher import StringMatcher, StringMatcherDdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable


def new_with_transformation(transformer: StringTransformerResolver,
                            original: StringMatcherResolver) -> StringMatcherResolver:
    return _StringMatcherWithTransformationResolver(transformer, original)


def new_reference(name_of_referenced_resolver: str,
                  expectation_type: ExpectationType) -> StringMatcherResolver:
    return StringMatcherReferenceResolver(name_of_referenced_resolver, expectation_type)


class StringMatcherConstantResolver(StringMatcherResolver):
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


class StringMatcherConstantOfValueResolver(StringMatcherResolver):
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


class _StringMatcherWithTransformationResolver(StringMatcherResolver):
    """
    A :class:`StringMatcherResolver` that transforms the model with a :class:`StringTransformerResolver`
    """

    def __init__(self,
                 transformer: StringTransformerResolver,
                 original: StringMatcherResolver,
                 ):
        self._transformer = transformer
        self._original = original
        self._validator = pre_or_post_validation.AndValidator([
            pre_or_post_validation.PreOrPostSdsValidatorFromValueValidator(
                lambda symbols: transformer.resolve(symbols).validator()
            ),
            original.validator,
        ])

    def resolve(self, symbols: SymbolTable) -> StringMatcherDdv:
        return string_matchers.StringMatcherWithTransformationDdv(
            self._transformer.resolve(symbols),
            self._original.resolve(symbols),
        )

    @property
    def references(self) -> Sequence[SymbolReference]:
        return list(self._transformer.references) + list(self._original.references)

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def __str__(self):
        return str(type(self))


class StringMatcherResolverFromParts2(StringMatcherResolver):
    def __init__(self,
                 references: Sequence[SymbolReference],
                 validator: PreOrPostSdsValidator,
                 get_matcher_value: Callable[[SymbolTable], StringMatcherDdv]):
        self._get_matcher_value = get_matcher_value
        self._validator = validator
        self._references = references

    def resolve(self, symbols: SymbolTable) -> StringMatcherDdv:
        return self._get_matcher_value(symbols)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def __str__(self):
        return str(type(self))


class StringMatcherReferenceResolver(StringMatcherResolver):
    """
    A :class:`StringMatcherResolver` that is a reference to a symbol
    """

    def __init__(self,
                 name_of_referenced_resolver: str,
                 expectation_type: ExpectationType):
        self._name_of_referenced_resolver = name_of_referenced_resolver
        self._references = [SymbolReference(name_of_referenced_resolver,
                                            ValueTypeRestriction(ValueType.STRING_MATCHER))]
        self._expectation_type = expectation_type
        self._validator = _ValidatorOfReferredResolver(name_of_referenced_resolver)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def resolve(self, symbols: SymbolTable) -> StringMatcherDdv:
        resolver = lookups.lookup_string_matcher(symbols,
                                                 self._name_of_referenced_resolver)
        referenced_value = resolver.resolve(symbols)

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
        return str(type(self)) + '\'' + str(self._name_of_referenced_resolver) + '\''


class _ValidatorOfReferredResolver(pre_or_post_validation.ValidatorOfReferredResolverBase):
    def _referred_validator(self, environment: PathResolvingEnvironment) -> PreOrPostSdsValidator:
        referred_matcher_resolver = lookups.lookup_string_matcher(environment.symbols, self.symbol_name)
        return referred_matcher_resolver.validator
