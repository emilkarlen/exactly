from typing import Generic

from exactly_lib.definitions import logic
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.matcher_base_class import MODEL, MatcherWTrace
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.util.description_tree import renderers, tree


class MatcherWithConstantResult(Generic[MODEL], MatcherWTrace[MODEL]):
    def __init__(self, result: bool):
        self._result = result
        self._matching_result = MatchingResult(
            self._result,
            renderers.Constant(
                tree.Node(logic.CONSTANT_MATCHER,
                          self._result,
                          (tree.StringDetail(logic.BOOLEANS[result]),),
                          ())
            ),
        )
        self._structure = renderers.Constant(
            tree.Node(logic.CONSTANT_MATCHER, None,
                      (tree.StringDetail(logic.BOOLEANS[result]),),
                      ())
        )

    @property
    def name(self) -> str:
        return logic.CONSTANT_MATCHER

    def structure(self) -> StructureRenderer:
        return self._structure

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        return self._matching_result
