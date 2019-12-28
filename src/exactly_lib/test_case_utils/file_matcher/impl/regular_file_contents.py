from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.test_case import file_check_properties
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils import file_properties, path_check
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.file_matcher.impl.base_class import FileMatcherDdvImplBase, FileMatcherImplBase, \
    FileMatcherAdvImplBase
from exactly_lib.test_case_utils.matcher.impls import sdv_components
from exactly_lib.test_case_utils.string_transformer.impl import identity
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic import string_matcher
from exactly_lib.type_system.logic.file_matcher import FileMatcherDdv, FileMatcherModel, FileMatcherSdvType
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
        self._is_regular_file_check = file_properties.must_exist_as(file_properties.FileType.REGULAR,
                                                                    follow_symlinks=True)

    @property
    def name(self) -> str:
        return self.NAME

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
        mb_failure = path_check.failure_message_or_none(self._is_regular_file_check, model.path)
        if mb_failure:
            raise HardErrorException(mb_failure)

    @staticmethod
    def _string_matcher_model(model: FileMatcherModel) -> string_matcher.FileToCheck:
        return string_matcher.FileToCheck(
            model.path,
            identity.IdentityStringTransformer(),
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


def regular_file_matches_string_matcher_sdv__generic(contents_matcher: StringMatcherSdv) -> FileMatcherSdvType:
    def make_ddv(symbols: SymbolTable) -> FileMatcherDdv:
        contents_matcher_ddv = contents_matcher.resolve(symbols)
        return RegularFileMatchesStringMatcherDdv(contents_matcher_ddv)

    return sdv_components.MatcherSdvFromParts(
        contents_matcher.references,
        make_ddv,
    )
