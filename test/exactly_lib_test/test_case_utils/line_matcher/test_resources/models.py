from typing import Callable, List, Sequence

from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_system.logic.line_matcher import LineMatcherLine, FIRST_LINE_NUMBER
from exactly_lib_test.test_case_utils.line_matcher.test_resources import assertions
from exactly_lib_test.test_case_utils.matcher.test_resources import integration_check as matcher_integration_check

ModelConstructor = Callable[[FullResolvingEnvironment], LineMatcherLine]

ARBITRARY_MODEL = matcher_integration_check.constant_model(
    assertions.validated((1, 'arbitrary model line'))
)


def constant(model: LineMatcherLine) -> ModelConstructor:
    return matcher_integration_check.constant_model(
        assertions.validated(model)
    )


def models_for_lines__validated(lines: Sequence[str]) -> List[LineMatcherLine]:
    return [
        assertions.validated((num, contents))
        for num, contents in enumerate(lines, start=FIRST_LINE_NUMBER)
    ]
