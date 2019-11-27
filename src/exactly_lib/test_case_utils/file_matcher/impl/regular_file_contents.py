from typing import List, Optional

from exactly_lib.common.report_rendering import text_docs__old
from exactly_lib.definitions import actual_file_attributes
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.test_case import file_check_properties
from exactly_lib.symbol.logic.file_matcher import FileMatcherSdv
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case.validation.ddv_validators import DdvValidatorFromSdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_matcher.impl.impl_base_class import FileMatcherImplBase
from exactly_lib.test_case_utils.file_system_element_matcher import ErrorMessageResolverForFailingFileProperties2
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic import string_matcher
from exactly_lib.type_system.logic import string_transformer
from exactly_lib.type_system.logic.file_matcher import FileMatcherDdv, FileMatcher, FileMatcherModel
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.symbol_table import SymbolTable


class RegularFileMatchesStringMatcher(FileMatcherImplBase):
    NAME = ' '.join((file_check_properties.REGULAR_FILE_CONTENTS,
                     syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT.singular_name)
                    )

    def __init__(self, string_matcher: string_matcher.StringMatcher):
        super().__init__()
        self._string_matcher = string_matcher
        self._expected_file_type = file_properties.FileType.REGULAR
        self._is_regular_file_check = file_properties.ActualFilePropertiesResolver(self._expected_file_type,
                                                                                   follow_symlinks=True)

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def option_description(self) -> str:
        return 'contents matches STRING-MATCHER'

    def matches(self, model: FileMatcherModel) -> bool:
        return self.matches_emr(model) is None

    def matches_emr(self, model: FileMatcherModel) -> Optional[ErrorMessageResolver]:
        self._hard_error_if_not_regular_file(model)
        model = self._string_matcher_model(model)
        return self._string_matcher.matches_emr(model)

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        self._hard_error_if_not_regular_file(model)

        sm_model = self._string_matcher_model(model)
        sm_result = self._string_matcher.matches_w_trace(sm_model)
        return (
            self._new_tb()
                .append_child(sm_result.trace)
                .build_result(sm_result.value)
        )

    def _hard_error_if_not_regular_file(self, model: FileMatcherModel):
        failure_info_properties = self._is_regular_file_check.resolve_failure_info(model.path.primitive)
        if failure_info_properties:
            property_descriptor = model.file_descriptor.construct_for_contents_attribute(
                actual_file_attributes.TYPE_ATTRIBUTE
            )
            raise HardErrorException(
                text_docs__old.of_err_msg_resolver(
                    ErrorMessageResolverForFailingFileProperties2(property_descriptor,
                                                                  failure_info_properties,
                                                                  self._expected_file_type)
                ))

    @staticmethod
    def _string_matcher_model(model: FileMatcherModel) -> string_matcher.FileToCheck:
        return string_matcher.FileToCheck(
            model.path,
            model.file_descriptor,
            model.tmp_file_space,
            string_transformer.IdentityStringTransformer(),
            string_matcher.DestinationFilePathGetter(),
        )

    def _structure(self) -> StructureRenderer:
        return (
            self._new_structure_builder()
                .append_details(self._details_renderer_of(self._string_matcher))
                .build()
        )


class RegularFileMatchesStringMatcherDdv(FileMatcherDdv):
    def __init__(self,
                 contents_matcher: string_matcher.StringMatcherDdv,
                 validator: DdvValidator):
        self._contents_matcher = contents_matcher
        self._validator = validator

    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> FileMatcher:
        return RegularFileMatchesStringMatcher(self._contents_matcher.value_of_any_dependency(tcds))


class RegularFileMatchesStringMatcherSdv(FileMatcherSdv):
    def __init__(self, contents_matcher: StringMatcherSdv):
        self._contents_matcher = contents_matcher

    @property
    def references(self) -> List[SymbolReference]:
        return self._contents_matcher.references

    def resolve(self, symbols: SymbolTable) -> FileMatcherDdv:
        return RegularFileMatchesStringMatcherDdv(
            self._contents_matcher.resolve(symbols),
            DdvValidatorFromSdvValidator(
                symbols,
                self._contents_matcher.validator
            )
        )
