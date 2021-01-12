from typing import Sequence

from exactly_lib.impls.description_tree.tree_structured import WithCachedNodeDescriptionBase
from exactly_lib.impls.types.string_transformer import names
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironment, \
    ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validators
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerAdv, StringTransformerDdv
from exactly_lib.type_val_prims import string_transformer_descr
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_transformer import StringTransformer


class SequenceStringTransformer(WithCachedNodeDescriptionBase, StringTransformer):
    NAME = names.SEQUENCE_OPERATOR_NAME

    def __init__(self, transformers: Sequence[StringTransformer]):
        super().__init__()
        self._transformers = tuple(transformers)
        self._non_identity_transformer_functions = [
            transformer.transform
            for transformer in transformers
            if not transformer.is_identity_transformer
        ]
        self._is_identity = len(self._non_identity_transformer_functions) == 0

    @property
    def name(self) -> str:
        return self.NAME

    def _structure(self) -> StructureRenderer:
        return string_transformer_descr.sequence_of_at_least_2_operands(self._transformers)

    @property
    def is_identity_transformer(self) -> bool:
        return self._is_identity

    def transform(self, model: StringSource) -> StringSource:
        for transformer in self._non_identity_transformer_functions:
            model = transformer(model)
        return model

    def __str__(self):
        return '{}[{}]'.format(type(self).__name__,
                               ','.join(map(str, self._transformers)))


class _StringTransformerSequenceAdv(ApplicationEnvironmentDependentValue[StringTransformer]):
    def __init__(self, transformers: Sequence[StringTransformerAdv]):
        self._transformers = transformers

    def primitive(self, environment: ApplicationEnvironment) -> StringTransformer:
        return SequenceStringTransformer([
            transformer.primitive(environment)
            for transformer in self._transformers
        ])


class StringTransformerSequenceDdv(StringTransformerDdv):
    def __init__(self, transformers: Sequence[StringTransformerDdv]):
        self._transformers = transformers
        self._validator = ddv_validators.AndValidator([
            transformer.validator
            for transformer in transformers
        ])

    def structure(self) -> StructureRenderer:
        return string_transformer_descr.sequence_of_at_least_2_operands(self._transformers)

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> StringTransformerAdv:
        return _StringTransformerSequenceAdv([
            transformer.value_of_any_dependency(tcds)
            for transformer in self._transformers
        ])
