import functools
from typing import Sequence

from exactly_lib.definitions.entity import types
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.sdv_structure import SymbolReference, references_from_objects_with_symbol_references
from exactly_lib.test_case_file_structure import ddv_validators
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.expression.grammar_elements import OperatorExpressionDescriptionFromFunctions
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
from exactly_lib.util.textformat.textformat_parser import TextParser


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

    def primitive(self, environment: ApplicationEnvironment) -> StringTransformer:
        return SequenceStringTransformer([
            transformer.primitive(environment)
            for transformer in self._transformers
        ])


class _StringTransformerSequenceDdv(StringTransformerDdv):
    def __init__(self, transformers: Sequence[StringTransformerDdv]):
        self._transformers = transformers
        self._validator = ddv_validators.AndValidator([
            transformer.validator
            for transformer in transformers
        ])

    def structure(self) -> StructureRenderer:
        return SequenceStringTransformer.new_structure_tree(self._transformers)

    @property
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

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

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


_SEQUENCE_TRANSFORMER_SED_DESCRIPTION = """\
Sequence of two or more {_TRANSFORMERS_}.

The result of the {_TRANSFORMER_} to the left is feed to the
{_TRANSFORMER_} to the right.
"""

_TEXT_PARSER = TextParser({
    '_TRANSFORMER_': types.STRING_TRANSFORMER_TYPE_INFO.name.singular,
    '_TRANSFORMERS_': types.STRING_TRANSFORMER_TYPE_INFO.name.plural,

})

SYNTAX_DESCRIPTION = OperatorExpressionDescriptionFromFunctions(
    _TEXT_PARSER.fnap__fun(_SEQUENCE_TRANSFORMER_SED_DESCRIPTION)
)
