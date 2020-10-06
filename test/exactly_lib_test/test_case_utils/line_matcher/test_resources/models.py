from typing import Callable

from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_system.logic.line_matcher import LineMatcherLine
from exactly_lib_test.test_case_utils.matcher.test_resources import integration_check as matcher_integration_check

ModelConstructor = Callable[[FullResolvingEnvironment], LineMatcherLine]


def validated(model: LineMatcherLine) -> LineMatcherLine:
    line_num = model[0]
    if not isinstance(line_num, int):
        raise ValueError('Line number is not an int: ' + repr(model))
    if line_num <= 0:
        raise ValueError('Line number is <= 0: ' + repr(model))

    contents = model[1]
    if not isinstance(contents, str):
        raise ValueError('Line contents is not an str: ' + repr(model))
    if contents.find('\n') != -1:
        raise ValueError('Line contents contains new-line: ' + repr(model))

    return model


ARBITRARY_MODEL = matcher_integration_check.constant_model(validated((1, 'arbitrary model line')))


def constant(model: LineMatcherLine) -> ModelConstructor:
    return matcher_integration_check.constant_model(validated(model))
