from typing import Sequence, Optional, Set

from exactly_lib.symbol.logic.string_transformer import StringTransformerResolver
from exactly_lib.symbol.symbol_usage import SymbolReference, SymbolUsage
from exactly_lib.test_case.pre_or_post_value_validation import PreOrPostSdsValueValidator, constant_success_validator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerValue, \
    StringTransformerModel
from exactly_lib.type_system.logic.string_transformer_values import StringTransformerConstantValue
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.symbols_setup import ResolverSymbolContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class StringTransformerConstantTestImpl(StringTransformer):
    """Matcher with constant result."""

    def __init__(self, result: StringTransformerModel):
        self._result = result

    def is_identity_transformer(self) -> bool:
        return False

    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        return self._result


class StringTransformerIdentityTestImpl(StringTransformer):
    """Matcher with no modification."""

    def is_identity_transformer(self) -> bool:
        return True

    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        return lines


class StringTransformerConstantSequenceTestImpl(StringTransformer):
    """Matcher with constant result."""

    def __init__(self, result: Sequence[str]):
        self._result = result

    def is_identity_transformer(self) -> bool:
        return False

    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        return iter(self._result)


class StringTransformerValueTestImpl(StringTransformerValue):
    def __init__(self,
                 primitive_value: StringTransformer,
                 validator: PreOrPostSdsValueValidator = constant_success_validator(),
                 resolving_dependencies: Optional[Set[DirectoryStructurePartition]] = None):
        self._primitive_value = primitive_value
        self._validator = validator
        self._resolving_dependencies = (set()
                                        if resolving_dependencies is None
                                        else resolving_dependencies)

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._resolving_dependencies

    def validator(self) -> PreOrPostSdsValueValidator:
        return self._validator

    def value_when_no_dir_dependencies(self) -> StringTransformer:
        return self._primitive_value

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> StringTransformer:
        return self._primitive_value


class StringTransformerResolverConstantTestImpl(StringTransformerResolver):
    def __init__(self,
                 resolved_value: StringTransformer,
                 references: Sequence[SymbolReference] = ()):
        self._resolved_value = resolved_value
        self._references = list(references)

    @property
    def resolved_value(self) -> StringTransformer:
        return self._resolved_value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> StringTransformerValue:
        return StringTransformerConstantValue(self._resolved_value)


class StringTransformerResolverConstantValueTestImpl(StringTransformerResolver):
    def __init__(self,
                 resolved_value: StringTransformerValue,
                 references: Sequence[SymbolReference] = ()):
        self._resolved_value = resolved_value
        self._references = list(references)

    @property
    def resolved_value(self) -> StringTransformer:
        return self._resolved_value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> StringTransformerValue:
        return self._resolved_value


def string_transformer_from_primitive_value(primitive_value: StringTransformer = StringTransformerIdentityTestImpl(),
                                            references: Sequence[SymbolReference] = (),
                                            validator: PreOrPostSdsValueValidator = constant_success_validator(),
                                            ) -> StringTransformerResolver:
    return StringTransformerResolverConstantValueTestImpl(
        StringTransformerValueTestImpl(
            primitive_value,
            validator
        ),
        references=references,
    )


def string_transformer_from_result(result: StringTransformerModel,
                                   references: Sequence[SymbolReference] = (),
                                   validator: PreOrPostSdsValueValidator = constant_success_validator(),
                                   ) -> StringTransformerResolver:
    return StringTransformerResolverConstantValueTestImpl(
        StringTransformerValueTestImpl(
            StringTransformerConstantTestImpl(result),
            validator
        ),
        references=references,
    )


def string_transformer_from_repeatable_result(result: Sequence[str],
                                              references: Sequence[SymbolReference] = (),
                                              validator: PreOrPostSdsValueValidator = constant_success_validator(),
                                              ) -> StringTransformerResolver:
    return StringTransformerResolverConstantValueTestImpl(
        StringTransformerValueTestImpl(
            StringTransformerConstantSequenceTestImpl(result),
            validator
        ),
        references=references,
    )


class StringTransformerSymbolContext(ResolverSymbolContext[StringTransformerResolver]):
    def __init__(self,
                 name: str,
                 resolver: StringTransformerResolver):
        super().__init__(name)
        self._resolver = resolver

    @property
    def resolver(self) -> StringTransformerResolver:
        return self._resolver

    @property
    def reference_assertion(self) -> ValueAssertion[SymbolReference]:
        return is_reference_to_string_transformer__ref(self.name)


def model_with_num_lines(number_of_lines: int) -> StringTransformerModel:
    return iter(['line'] * number_of_lines)


def arbitrary_transformer() -> StringTransformer:
    return StringTransformerIdentityTestImpl()


def arbitrary_transformer_value() -> StringTransformerValue:
    return StringTransformerValueTestImpl(arbitrary_transformer())


def arbitrary_transformer_resolver() -> StringTransformerResolver:
    return string_transformer_from_primitive_value(arbitrary_transformer())


IS_STRING_TRANSFORMER_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.STRING_TRANSFORMER)


def is_reference_to_string_transformer(name_of_transformer: str) -> ValueAssertion[SymbolUsage]:
    return asrt_sym_usage.matches_reference(asrt.equals(name_of_transformer),
                                            IS_STRING_TRANSFORMER_REFERENCE_RESTRICTION)


def is_reference_to_string_transformer__ref(name_of_transformer: str) -> ValueAssertion[SymbolReference]:
    return asrt.is_instance_with(SymbolReference,
                                 asrt_sym_usage.matches_reference(asrt.equals(name_of_transformer),
                                                                  IS_STRING_TRANSFORMER_REFERENCE_RESTRICTION)
                                 )
