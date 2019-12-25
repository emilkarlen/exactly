from exactly_lib.test_case_utils.string_matcher.base_class import StringMatcherImplBase
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.type_system.logic.string_matcher import FileToCheck


class StringMatcherTestImplBase(StringMatcherImplBase):
    def matches_w_trace(self, model: FileToCheck) -> MatchingResult:
        self._matches_side_effects(model)
        return self._new_tb().build_result(True)

    def _matches_side_effects(self, model: FileToCheck):
        pass
