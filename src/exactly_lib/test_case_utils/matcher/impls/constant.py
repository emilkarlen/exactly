from typing import Generic

from exactly_lib.definitions.primitives import boolean
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MODEL, MatchingResult
from exactly_lib.util.description_tree import renderers, tree


class MatcherWithConstantResult(Generic[MODEL], MatcherWTraceAndNegation[MODEL]):
    NAME = 'constant'

    def __init__(self, result: bool):
        self._result = result
        self._matching_result = MatchingResult(
            self._result,
            renderers.Constant(
                tree.Node(self.NAME, self._result,
                          (tree.StringDetail(boolean.BOOLEANS[result]),),
                          ())
            ),
        )
        self._structure = renderers.Constant(
            tree.Node(self.NAME, None,
                      (tree.StringDetail(boolean.BOOLEANS[result]),),
                      ())
        )

    @property
    def name(self) -> str:
        return self.NAME

    def structure(self) -> StructureRenderer:
        return self._structure

    @property
    def negation(self) -> 'MatcherWithConstantResult[MODEL]':
        return MatcherWithConstantResult(not self._result)

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        return self._matching_result
