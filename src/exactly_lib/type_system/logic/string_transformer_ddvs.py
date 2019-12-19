from typing import Sequence, Callable

from exactly_lib.test_case.validation import ddv_validators
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic import string_transformer
from exactly_lib.type_system.logic.impls import advs
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue, ApplicationEnvironment
from exactly_lib.type_system.logic.string_transformer import StringTransformerDdv, StringTransformer, \
    StringTransformerAdv


class StringTransformerConstantDdv(StringTransformerDdv):
    """
    A :class:`StringTransformerResolver` that is a constant :class:`StringTransformer`
    """

    def __init__(self, value: StringTransformer):
        self._value = value

    def value_of_any_dependency(self, tcds: Tcds) -> StringTransformerAdv:
        return advs.ConstantAdv(self._value)


class StringTransformerSequenceAdv(ApplicationEnvironmentDependentValue[StringTransformer]):
    def __init__(self, transformers: Sequence[StringTransformerAdv]):
        self._transformers = transformers

    def applier(self, environment: ApplicationEnvironment) -> StringTransformer:
        return string_transformer.SequenceStringTransformer([
            transformer.applier(environment)
            for transformer in self._transformers
        ])


class StringTransformerSequenceDdv(StringTransformerDdv):
    def __init__(self, transformers: Sequence[StringTransformerDdv]):
        self._transformers = transformers
        self._validator = ddv_validators.AndValidator([
            transformer.validator()
            for transformer in transformers
        ])

    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> StringTransformerSequenceAdv:
        return StringTransformerSequenceAdv([
            transformer.value_of_any_dependency(tcds)
            for transformer in self._transformers
        ])


class DirDependentStringTransformerDdv(StringTransformerDdv):
    def __init__(self, constructor: Callable[[Tcds], StringTransformer]):
        self._constructor = constructor

    def value_of_any_dependency(self, tcds: Tcds) -> StringTransformerAdv:
        return advs.ConstantAdv(self._constructor(tcds))
