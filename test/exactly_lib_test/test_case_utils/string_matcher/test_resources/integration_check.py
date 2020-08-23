from typing import Callable

from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.test_case_utils.string_matcher import parse_string_matcher
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib_test.test_case_utils.logic.test_resources import integration_check
from exactly_lib_test.test_case_utils.matcher.test_resources.matcher_checker import \
    MatcherPropertiesConfiguration
from exactly_lib_test.type_system.logic.string_model.test_resources import string_models

ModelConstructor = Callable[[FullResolvingEnvironment], StringModel]


def empty_model() -> ModelConstructor:
    return model_of('')


def model_of(contents: str) -> ModelConstructor:
    return _ModelConstructorHelper(contents).construct


def model_that_must_not_be_used(environment: FullResolvingEnvironment) -> StringModel:
    return MODEL_THAT_MUST_NOT_BE_USED


def arbitrary_model() -> ModelConstructor:
    return empty_model()


CHECKER__PARSE_FULL = integration_check.IntegrationChecker(
    parse_string_matcher.parsers().full,
    MatcherPropertiesConfiguration(),
    False,
)

CHECKER__PARSE_SIMPLE = integration_check.IntegrationChecker(
    parse_string_matcher.parsers().simple,
    MatcherPropertiesConfiguration(),
    False,
)

MODEL_THAT_MUST_NOT_BE_USED = string_models.StringModelThatMustNotBeUsed()


class _ModelConstructorHelper:
    def __init__(self, contents: str):
        self.contents = contents

    def construct(self, environment: FullResolvingEnvironment) -> StringModel:
        return string_models.of_string(
            self.contents,
            environment.application_environment.tmp_files_space.sub_dir_space(),
        )
