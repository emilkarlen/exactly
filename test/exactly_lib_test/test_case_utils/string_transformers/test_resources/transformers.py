import re
from typing import Iterable

from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherRegex
from exactly_lib.test_case_utils.string_transformer.transformers import ReplaceStringTransformer, \
    SelectStringTransformer
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.type_system.logic.string_transformer import CustomStringTransformer


def replace_transformer(regex_str: str, replacement_str: str) -> ReplaceStringTransformer:
    return ReplaceStringTransformer(re.compile(regex_str),
                                    replacement_str)


def select_regex_transformer(regex_str: str) -> SelectStringTransformer:
    return select_transformer(LineMatcherRegex(re.compile(regex_str)))


def select_transformer(line_matcher: LineMatcher) -> SelectStringTransformer:
    return SelectStringTransformer(line_matcher)


class CustomStringTransformerTestImpl(CustomStringTransformer):
    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        raise NotImplementedError('should not be used')
