from exactly_lib.test_case_utils.matcher.impls.impl_base_class import MatcherImplBase
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.matching_result import MatchingResult


class FileMatcherThatMatchesAnyFileWhosNameStartsWith(MatcherImplBase[FileMatcherModel]):
    def __init__(self, prefix_of_name_for_match: str):
        super().__init__()
        self._prefix_of_name_for_match = prefix_of_name_for_match

    @property
    def name(self) -> str:
        return str(type(self))

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        return self._new_tb().build_result(
            model.path.primitive.name.startswith(self._prefix_of_name_for_match)
        )
