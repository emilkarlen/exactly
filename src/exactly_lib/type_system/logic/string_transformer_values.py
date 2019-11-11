from typing import Sequence, Callable

from exactly_lib.test_case.validation import pre_or_post_value_validators
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system.logic import string_transformer
from exactly_lib.type_system.logic.string_transformer import StringTransformerValue, StringTransformer


class StringTransformerConstantValue(StringTransformerValue):
    """
    A :class:`StringTransformerResolver` that is a constant :class:`StringTransformer`
    """

    def __init__(self, value: StringTransformer):
        self._value = value

    def value_when_no_dir_dependencies(self) -> StringTransformer:
        return self._value

    def value_of_any_dependency(self, tcds: HomeAndSds) -> StringTransformer:
        return self._value


class StringTransformerSequenceValue(StringTransformerValue):
    def __init__(self, transformers: Sequence[StringTransformerValue]):
        self._transformers = transformers
        self._validator = pre_or_post_value_validators.AndValidator([
            transformer.validator()
            for transformer in transformers
        ])

    def validator(self) -> PreOrPostSdsValueValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: HomeAndSds) -> string_transformer.SequenceStringTransformer:
        return string_transformer.SequenceStringTransformer([
            transformer.value_of_any_dependency(tcds)
            for transformer in self._transformers
        ])


class DirDependentStringTransformerValue(StringTransformerValue):
    def __init__(self, constructor: Callable[[HomeAndSds], StringTransformer]):
        self._constructor = constructor

    def value_of_any_dependency(self, tcds: HomeAndSds) -> StringTransformer:
        return self._constructor(tcds)
