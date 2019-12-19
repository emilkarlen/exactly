from typing import Optional

from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.test_case.validation import ddv_validators
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.string_matcher.base_class import StringMatcherImplBase, StringMatcherDdvImplBase, \
    StringMatcherAdvImplBase
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, ApplicationEnvironment, \
    MatcherWTraceAndNegation, MODEL, MatcherAdv
from exactly_lib.type_system.logic.string_matcher import StringMatcher, FileToCheck, StringMatcherDdv, StringMatcherAdv
from exactly_lib.type_system.logic.string_transformer import StringTransformer, SequenceStringTransformer, \
    StringTransformerDdv, StringTransformerAdv
from exactly_lib.util.description_tree import renderers, details


class StringMatcherOnTransformedFileToCheck(StringMatcherImplBase):
    """Applies a string transformer to the file to check."""

    NAME = ' '.join((instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION,
                     syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.singular_name))

    def __init__(self,
                 transformer: StringTransformer,
                 on_transformed: StringMatcher):
        super().__init__()
        self._transformer = transformer
        self._on_transformed = on_transformed
        self._transformer_detail = details.Tree(self._transformer.structure())

    @property
    def name(self) -> str:
        return self.NAME

    @staticmethod
    def new_structure_tree(transformer: StructureRenderer,
                           on_transformed: StructureRenderer) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            StringMatcherOnTransformedFileToCheck.NAME,
            None,
            (details.Tree(transformer),),
            (on_transformed,),
        )

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(self._transformer.structure(),
                                       self._on_transformed.structure())

    @property
    def option_description(self) -> str:
        return 'transformed: ' + self._on_transformed.option_description

    def matches_emr(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        complete_transformer = self._complete_transformer(model)
        transformed_model = model.with_transformation(complete_transformer)
        return self._on_transformed.matches_emr(transformed_model)

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

    def applier(self, environment: ApplicationEnvironment) -> MatcherWTraceAndNegation[MODEL]:
        return StringMatcherOnTransformedFileToCheck(self._transformer.applier(environment),
                                                     self._on_transformed.applier(environment),
                                                     )


class StringMatcherWithTransformationDdv(StringMatcherDdvImplBase):
    def __init__(self,
                 transformer: StringTransformerDdv,
                 on_transformed: StringMatcherDdv,
                 ):
        self._transformer = transformer
        self._on_transformed = on_transformed
        self._validator = ddv_validators.AndValidator([
            transformer.validator(),
            on_transformed.validator,
        ])

    def structure(self) -> StructureRenderer:
        return StringMatcherOnTransformedFileToCheck.new_structure_tree(
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
