from exactly_lib.test_case_utils.string_matcher.impl.base_class import StringMatcherImplBase
from exactly_lib.type_system.description.structure_building import StructureBuilder
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.type_system.logic.string_model import StringModel


class EqualsConstant(StringMatcherImplBase):
    def __init__(self, expected: str):
        super().__init__()
        self._expected = expected

    def matches_w_trace(self, model: StringModel) -> MatchingResult:
        actual = self._as_string(model)
        return TraceBuilder(self.name).build_result(self._expected == actual)

    @staticmethod
    def _as_string(model: StringModel) -> str:
        with model.as_lines as lines_iter:
            return ''.join(lines_iter)

    @property
    def name(self) -> str:
        return str(type(self))

    def _structure(self) -> StructureRenderer:
        return StructureBuilder(self.name).as_render()
