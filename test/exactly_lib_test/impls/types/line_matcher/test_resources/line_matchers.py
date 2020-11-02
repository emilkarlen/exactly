from typing import List

from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcherLine
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib_test.impls.types.matcher.test_resources.matchers import ConstantMatcherWithCustomName


class LineMatcherThatCollectsModels(ConstantMatcherWithCustomName[LineMatcherLine]):
    def __init__(self,
                 output: List[LineMatcherLine],
                 result: bool,
                 ):
        super().__init__('models-collector', result)
        self.output = output

    def matches_w_trace(self, model: LineMatcherLine) -> MatchingResult:
        self.output.append(model)
        return super().matches_w_trace(model)
