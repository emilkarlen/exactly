from typing import List

from exactly_lib.symbol.logic.logic_value_resolver import LogicValueResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case import pre_or_post_validation
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.type_system.logic.string_matcher import StringMatcherValue
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util.symbol_table import SymbolTable


class StringMatcherResolver(LogicValueResolver):
    """ Base class for resolvers of :class:`StringMatcherValue`. """

    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.STRING_MATCHER

    @property
    def value_type(self) -> ValueType:
        return ValueType.STRING_MATCHER

    @property
    def references(self) -> List[SymbolReference]:
        raise NotImplementedError('abstract method')

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return pre_or_post_validation.ConstantSuccessValidator()

    def resolve(self, symbols: SymbolTable) -> StringMatcherValue:
        raise NotImplementedError('abstract method')
