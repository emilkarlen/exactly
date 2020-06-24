from typing import Sequence

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure import ddv_validators
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.string_matcher.impl.base_class import StringMatcherImplBase, StringMatcherDdvImplBase, \
    StringMatcherAdvImplBase
from exactly_lib.test_case_utils.string_transformer.impl.sequence import SequenceStringTransformer
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, ApplicationEnvironment, \
    MODEL, MatcherAdv, MatcherDdv, MatcherWTrace
from exactly_lib.type_system.logic.string_matcher import StringMatcher, FileToCheck, StringMatcherDdv, StringMatcherAdv, \
    StringMatcherSdv
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerDdv, \
    StringTransformerAdv
from exactly_lib.util.description_tree import renderers, details
from exactly_lib.util.symbol_table import SymbolTable


class StringMatcherWithTransformation(StringMatcherImplBase):
    """Applies a string transformer to the file to check."""

    NAME = ' '.join((string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION,
                     syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.singular_name))

    def __init__(self,
                 transformer: StringTransformer,
                 on_transformed: StringMatcher):
        super().__init__()
        self._transformer = transformer
        self._on_transformed = on_transformed
        self._transformer_detail = custom_details.WithTreeStructure(self._transformer)

    @property
    def name(self) -> str:
        return self.NAME

    @staticmethod
    def new_structure_tree(transformer: StructureRenderer,
                           on_transformed: StructureRenderer) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            StringMatcherWithTransformation.NAME,
            None,
            (details.Tree(transformer),),
            (on_transformed,),
        )

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(self._transformer.structure(),
                                       self._on_transformed.structure())

    def _complete_transformer(self, model: FileToCheck) -> StringTransformer:
        if model.string_transformer.is_identity_transformer:
            return self._transformer
        else:
            return SequenceStringTransformer([
                model.string_transformer,
                self._transformer,
            ])

    def matches_w_trace(self, model: FileToCheck) -> MatchingResult:
        complete_transformer = self._complete_transformer(model)
        transformed_model = model.with_transformation(complete_transformer)
        result_on_transformed = self._on_transformed.matches_w_trace(transformed_model)
        return (
            self._new_tb()
                .append_details(self._transformer_detail)
                .append_child(result_on_transformed.trace)
                .build_result(result_on_transformed.value)
        )


class _StringMatcherWithTransformationAdv(StringMatcherAdvImplBase):
    def __init__(self,
                 transformer: StringTransformerAdv,
                 on_transformed: StringMatcherAdv,
                 ):
        self._transformer = transformer
        self._on_transformed = on_transformed

    def primitive(self, environment: ApplicationEnvironment) -> MatcherWTrace[MODEL]:
        return StringMatcherWithTransformation(self._transformer.primitive(environment),
                                               self._on_transformed.primitive(environment),
                                               )


class StringMatcherWithTransformationDdv(StringMatcherDdvImplBase):
    def __init__(self,
                 transformer: StringTransformerDdv,
                 on_transformed: StringMatcherDdv,
                 ):
        self._transformer = transformer
        self._on_transformed = on_transformed
        self._validator = ddv_validators.AndValidator([
            transformer.validator,
            on_transformed.validator,
        ])

    def structure(self) -> StructureRenderer:
        return StringMatcherWithTransformation.new_structure_tree(
            self._transformer.structure(),
            self._on_transformed.structure(),
        )

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        return _StringMatcherWithTransformationAdv(
            self._transformer.value_of_any_dependency(tcds),
            self._on_transformed.value_of_any_dependency(tcds),
        )


class StringMatcherWithTransformationSdv(MatcherSdv[FileToCheck]):
    """
    A :class:`StringMatcherResolver` that transforms the model with a :class:`StringTransformerResolver`
    """

    def __init__(self,
                 transformer: StringTransformerSdv,
                 original: StringMatcherSdv,
                 ):
        self._transformer = transformer
        self._original = original

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[FileToCheck]:
        return StringMatcherWithTransformationDdv(
            self._transformer.resolve(symbols),
            self._original.resolve(symbols),
        )

    @property
    def references(self) -> Sequence[SymbolReference]:
        return list(self._transformer.references) + list(self._original.references)

    def __str__(self):
        return str(type(self))
