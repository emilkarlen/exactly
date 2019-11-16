from typing import Sequence, Callable

from exactly_lib.test_case.validation import pre_or_post_value_validators
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic import string_transformer
from exactly_lib.type_system.logic.string_transformer import StringTransformerDdv, StringTransformer


class StringTransformerConstantDdv(StringTransformerDdv):
    """
    A :class:`StringTransformerResolver` that is a constant :class:`StringTransformer`
    """

    def __init__(self, value: StringTransformer):
        self._value = value

    def value_when_no_dir_dependencies(self) -> StringTransformer:
        return self._value

    def value_of_any_dependency(self, tcds: Tcds) -> StringTransformer:
        return self._value


class StringTransformerSequenceDdv(StringTransformerDdv):
    def __init__(self, transformers: Sequence[StringTransformerDdv]):
        self._transformers = transformers
        self._validator = pre_or_post_value_validators.AndValidator([
            transformer.validator()
            for transformer in transformers
        ])

    def validator(self) -> PreOrPostSdsValueValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> string_transformer.SequenceStringTransformer:
        return string_transformer.SequenceStringTransformer([
            transformer.value_of_any_dependency(tcds)
            for transformer in self._transformers
        ])


class DirDependentStringTransformerDdv(StringTransformerDdv):
    def __init__(self, constructor: Callable[[Tcds], StringTransformer]):
        self._constructor = constructor

    def value_of_any_dependency(self, tcds: Tcds) -> StringTransformer:
        return self._constructor(tcds)
