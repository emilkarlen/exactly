from exactly_lib.test_case_utils.matcher.property_matcher import PropertyMatcherDescriber
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, TraceRenderer
from exactly_lib.util.description_tree import renderers, details


class IdenticalToMatcher(PropertyMatcherDescriber):
    def trace(self, matcher_result: MatchingResult) -> TraceRenderer:
        return matcher_result.trace

    def structure(self, matcher: StructureRenderer) -> StructureRenderer:
        return matcher


class NamedWithMatcherAsChild(PropertyMatcherDescriber):
    def __init__(self, name: str):
        self._name = name

    def trace(self, matcher_result: MatchingResult) -> TraceRenderer:
        return renderers.NodeRendererFromParts(
            self._name,
            matcher_result.value,
            (),
            (matcher_result.trace,)
        )

    def structure(self, matcher: StructureRenderer) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            self._name,
            None,
            (),
            (matcher,)
        )


class NamedWithMatcherAsDetail(PropertyMatcherDescriber):
    def __init__(self, name: str):
        self._name = name

    def trace(self, matcher_result: MatchingResult) -> TraceRenderer:
        return renderers.NodeRendererFromParts(
            self._name,
            matcher_result.value,
            (details.Tree(matcher_result.trace),),
            ()
        )

    def structure(self, matcher: StructureRenderer) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            self._name,
            None,
            (details.Tree(matcher),),
            ()
        )
