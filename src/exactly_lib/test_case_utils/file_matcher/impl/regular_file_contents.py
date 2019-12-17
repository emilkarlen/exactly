from typing import Optional

from exactly_lib.common.report_rendering import text_docs__old
from exactly_lib.definitions import actual_file_attributes
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.test_case import file_check_properties
from exactly_lib.symbol.logic.file_matcher import FileMatcherSdv
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.file_matcher.impl.base_class import FileMatcherDdvImplBase, FileMatcherImplBase, \
    FileMatcherAdvImplBase
from exactly_lib.test_case_utils.file_system_element_matcher import ErrorMessageResolverForFailingFileProperties2
from exactly_lib.test_case_utils.matcher.impls import sdv_components
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic import string_matcher
from exactly_lib.type_system.logic import string_transformer
from exactly_lib.type_system.logic.file_matcher import FileMatcherDdv, FileMatcherModel
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, ApplicationEnvironment, \
    MatcherWTraceAndNegation, MODEL, MatcherAdv
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.symbol_table import SymbolTable


class RegularFileMatchesStringMatcher(FileMatcherImplBase):
    NAME = ' '.join((file_check_properties.REGULAR_FILE_CONTENTS,
                     syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT.singular_name)
                    )

    def __init__(self, contents_matcher: string_matcher.StringMatcher):
        super().__init__()
        self._contents_matcher = contents_matcher
        self._expected_file_type = file_properties.FileType.REGULAR
        self._is_regular_file_check = file_properties.ActualFilePropertiesResolver(self._expected_file_type,
                                                                                   follow_symlinks=True)

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def option_description(self) -> str:
        return 'contents matches STRING-MATCHER'

    @staticmethod
    def new_structure_tree(contents_matcher: DetailsRenderer) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            RegularFileMatchesStringMatcher.NAME,
            None,
            (contents_matcher,),
            (),
        )

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(custom_details.WithTreeStructure(self._contents_matcher))

    def matches(self, model: FileMatcherModel) -> bool:
        return self.matches_w_trace(model).value

    def matches_emr(self, model: FileMatcherModel) -> Optional[ErrorMessageResolver]:
        raise NotImplementedError('deprecated')

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        self._hard_error_if_not_regular_file(model)

        sm_model = self._string_matcher_model(model)
        sm_result = self._contents_matcher.matches_w_trace(sm_model)
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


class _RegularFileMatchesStringMatcherAdv(FileMatcherAdvImplBase):
    def __init__(self,
                 contents_matcher: string_matcher.StringMatcherAdv,
                 ):
        self._contents_matcher = contents_matcher

    def applier(self, environment: ApplicationEnvironment) -> MatcherWTraceAndNegation[MODEL]:
        return RegularFileMatchesStringMatcher(self._contents_matcher.applier(environment))


class RegularFileMatchesStringMatcherDdv(FileMatcherDdvImplBase):
    def __init__(self,
                 contents_matcher: string_matcher.StringMatcherDdv,
                 ):
        self._contents_matcher = contents_matcher

    def structure(self) -> StructureRenderer:
        return RegularFileMatchesStringMatcher.new_structure_tree(
            custom_details.WithTreeStructure(self._contents_matcher)
        )

    @property
    def validator(self) -> DdvValidator:
        return self._contents_matcher.validator

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        return _RegularFileMatchesStringMatcherAdv(self._contents_matcher.value_of_any_dependency(tcds))


def regular_file_matches_string_matcher_sdv(contents_matcher: StringMatcherSdv) -> FileMatcherSdv:
    def make_ddv(symbols: SymbolTable) -> FileMatcherDdv:
        contents_matcher_ddv = contents_matcher.resolve(symbols)
        return RegularFileMatchesStringMatcherDdv(contents_matcher_ddv)

    return FileMatcherSdv(
        sdv_components.MatcherSdvFromParts(
            contents_matcher.references,
            make_ddv,
        )
    )
