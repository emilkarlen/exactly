import functools
from typing import Sequence

from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import ddv_validators
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.string_transformer import names
from exactly_lib.test_case_utils.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.type_system.description.tree_structured import StructureRenderer, WithTreeStructureDescription
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue, ApplicationEnvironment
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerModel, \
    StringTransformerAdv, StringTransformerDdv
from exactly_lib.type_system.logic.string_transformer_ddvs import StringTransformerConstantDdv
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.functional import compose_first_and_second
from exactly_lib.util.symbol_table import SymbolTable


class SequenceStringTransformer(WithCachedTreeStructureDescriptionBase, StringTransformer):
    NAME = names.SEQUENCE_OPERATOR_NAME

    def __init__(self, transformers: Sequence[StringTransformer]):
        super().__init__()
        self._transformers = tuple(transformers)

    @staticmethod
    def new_structure_tree(operands: Sequence[WithTreeStructureDescription]) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            SequenceStringTransformer.NAME,
            None,
            (),
            [operand.structure() for operand in operands],
        )

    @property
    def name(self) -> str:
        return self.NAME

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(self._transformers)

    @property
    def is_identity_transformer(self) -> bool:
        return all([t.is_identity_transformer for t in self._transformers])

    @property
    def transformers(self) -> Sequence[StringTransformer]:
        return self._transformers

    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        if not self._transformers:
            return lines
        else:
            return self._sequenced_transformers()(lines)

    def _sequenced_transformers(self):
        lines_to_lines_transformers = [t.transform
                                       for t in self._transformers]

        return functools.reduce(compose_first_and_second, lines_to_lines_transformers)

    def __str__(self):
        return '{}[{}]'.format(type(self).__name__,
                               ','.join(map(str, self._transformers)))


class _StringTransformerSequenceAdv(ApplicationEnvironmentDependentValue[StringTransformer]):
    def __init__(self, transformers: Sequence[StringTransformerAdv]):
        self._transformers = transformers

    def applier(self, environment: ApplicationEnvironment) -> StringTransformer:
        return SequenceStringTransformer([
            transformer.applier(environment)
            for transformer in self._transformers
        ])


class _StringTransformerSequenceDdv(StringTransformerDdv):
    def __init__(self, transformers: Sequence[StringTransformerDdv]):
        self._transformers = transformers
        self._validator = ddv_validators.AndValidator([
            transformer.validator()
            for transformer in transformers
        ])

    def structure(self) -> StructureRenderer:
        return SequenceStringTransformer.new_structure_tree(self._transformers)

    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> StringTransformerAdv:
        return _StringTransformerSequenceAdv([
            transformer.value_of_any_dependency(tcds)
            for transformer in self._transformers
        ])


class StringTransformerSequenceSdv(StringTransformerSdv):
    def __init__(self, transformers: Sequence[StringTransformerSdv]):
        self.transformers = transformers
        self._references = references_from_objects_with_symbol_references(transformers)

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        num_transformers = len(self.transformers)
        if num_transformers == 0:
            return StringTransformerConstantDdv(IdentityStringTransformer())
        elif num_transformers == 1:
            return self.transformers[0].resolve(symbols)
        else:
            return _StringTransformerSequenceDdv([
                transformer.resolve(symbols)
                for transformer in self.transformers
            ])

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references
