from exactly_lib.impls.types.string_matcher.impl.base_class import StringMatcherImplBase
from exactly_lib.type_val_prims.description.structure_building import StructureBuilder
from exactly_lib.type_val_prims.description.trace_building import TraceBuilder
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.type_val_prims.string_source.string_source import StringSource


class EqualsConstant(StringMatcherImplBase):
    def __init__(self, expected: str):
        super().__init__()
        self._expected = expected

    def matches_w_trace(self, model: StringSource) -> MatchingResult:
        actual = model.contents().as_str
        return TraceBuilder(self.name).build_result(self._expected == actual)

    @property
    def name(self) -> str:
        return str(type(self))

    def _structure(self) -> StructureRenderer:
        return StructureBuilder(self.name).as_render()
