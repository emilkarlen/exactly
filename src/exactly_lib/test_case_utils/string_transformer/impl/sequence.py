from typing import Sequence, Callable

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
from exactly_lib.test_case_utils.string_transformer.impl.transformer_from_lines import \
    StringTransformerFromLinesTransformer
from exactly_lib.type_system.description.tree_structured import StructureRenderer, WithTreeStructureDescription
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerModel, \
    StringTransformerAdv, StringTransformerDdv
from exactly_lib.type_system.logic.string_transformer_ddvs import StringTransformerConstantDdv
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.util.textformat.textformat_parser import TextParser


class SequenceStringTransformer(WithCachedTreeStructureDescriptionBase, StringTransformerFromLinesTransformer):
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
        return self._is_identity

    @property
    def transformers(self) -> Sequence[StringTransformer]:
        return self._transformers

    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        return (
            lines
            if self._is_identity
            else
            self._sequenced_transformers()(lines)
        )

    def _sequenced_transformers(self) -> Callable[[StringTransformerModel], StringTransformerModel]:
        def ret_val_fun(model: StringTransformerModel) -> StringTransformerModel:
            ret_val = model
            for f in self._non_identity_transformer_functions:
                ret_val = f(ret_val)
            return ret_val

        return ret_val_fun

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
