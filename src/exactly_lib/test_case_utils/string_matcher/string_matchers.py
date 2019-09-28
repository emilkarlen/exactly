from typing import Optional

from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.type_system.logic.string_matcher import StringMatcher, FileToCheck
from exactly_lib.type_system.logic.string_transformer import StringTransformer, SequenceStringTransformer


class StringMatcherOnTransformedFileToCheck(StringMatcher):
    """Applies a string transformer to the file to check."""

    def __init__(self,
                 transformer: StringTransformer,
                 on_transformed: StringMatcher):
        self._transformer = transformer
        self._on_transformed = on_transformed

    @property
    def name(self) -> str:
        return ' '.join((
            instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME.long,
            syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.singular_name,
        ))

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
                .append_child(result_on_transformed.trace)
                .build_result(result_on_transformed.value)
        )
