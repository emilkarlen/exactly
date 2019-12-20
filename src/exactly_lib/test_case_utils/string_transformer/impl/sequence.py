import functools
from typing import Sequence

from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import ddv_validators
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue, ApplicationEnvironment
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerModel, \
    StringTransformerAdv, StringTransformerDdv
from exactly_lib.util.functional import compose_first_and_second
from exactly_lib.util.symbol_table import SymbolTable


class SequenceStringTransformer(StringTransformer):
    def __init__(self, transformers: Sequence[StringTransformer]):
        self._transformers = tuple(transformers)

    @property
    def name(self) -> str:
        return 'sequence'

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
        return _StringTransformerSequenceDdv([
            transformer.resolve(symbols)
            for transformer in self.transformers
        ])

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references
