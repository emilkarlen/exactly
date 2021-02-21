from typing import List, FrozenSet

from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcherLine
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib_test.impls.types.matcher.test_resources.matchers import ConstantMatcherWithCustomName, \
    MatcherTestImplBase
from exactly_lib_test.type_val_prims.matcher.test_resources import matching_result


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


class LineMatcherThatMatchesContentsSubString(MatcherTestImplBase[LineMatcherLine]):
    def __init__(self, sub_string: str):
        self._sub_string = sub_string

    def matches_w_trace(self, model: LineMatcherLine) -> MatchingResult:
        return matching_result.of(self._sub_string in model[1])


class LineMatcherThatMatchesLineNumbers(MatcherTestImplBase[LineMatcherLine]):
    def __init__(self, matching_line_numbers: FrozenSet[int]):
        self._matching_line_numbers = matching_line_numbers

    def matches_w_trace(self, model: LineMatcherLine) -> MatchingResult:
        return matching_result.of(model[0] in self._matching_line_numbers)
