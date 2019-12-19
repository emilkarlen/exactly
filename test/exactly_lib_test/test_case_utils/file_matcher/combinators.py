import pathlib
import unittest
from typing import List

from exactly_lib.test_case_utils.matcher.impls import combinator_matchers
from exactly_lib.test_case_utils.matcher.impls.impl_base_class import MatcherImplBase
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel, FileMatcher
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib_test.test_case_utils.file_matcher.test_resources import file_matcher_models as models
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_case_utils.test_resources import matcher_combinators_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestAnd),
        unittest.makeSuite(TestOr),
        unittest.makeSuite(TestNot),
    ])


class FileMatcherConfiguration(matcher_combinators_check.MatcherConfiguration):
    def irrelevant_model(self) -> FileMatcherModel:
        return models.new_model(pathlib.Path('irrelevant path'))

    def matcher_with_constant_result(self,
                                     name: str,
                                     result: bool) -> FileMatcher:
        return matchers.ConstantMatcherWithCustomName(name, result)

    def matcher_that_registers_model_argument_and_returns_constant(self,
                                                                   registry: List,
                                                                   result: bool) -> FileMatcher:
        return FileMatcherThatRegistersModelArgument(registry, result)


class TestAnd(matcher_combinators_check.TestAndBase):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> matcher_combinators_check.MatcherConfiguration:
        return FileMatcherConfiguration()

    def new_combinator_to_check(self, constructor_argument):
        return combinator_matchers.Conjunction(constructor_argument)


class TestOr(matcher_combinators_check.TestOrBase):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> matcher_combinators_check.MatcherConfiguration:
        return FileMatcherConfiguration()

    def new_combinator_to_check(self, constructor_argument):
        return combinator_matchers.Disjunction(constructor_argument)


class TestNot(matcher_combinators_check.TestNotBase):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> matcher_combinators_check.MatcherConfiguration:
        return FileMatcherConfiguration()

    def new_combinator_to_check(self, constructor_argument):
        return combinator_matchers.Negation(constructor_argument)


class FileMatcherThatRegistersModelArgument(MatcherImplBase[FileMatcherModel]):
    def __init__(self,
                 registry: List[FileMatcherModel],
                 constant_result: bool):
        MatcherImplBase.__init__(self)
        self._registry = registry
        self._constant_result = constant_result

    @property
    def name(self) -> str:
        return str(type(self))

    @property
    def option_description(self) -> str:
        raise NotImplementedError('this method should not be used')

    def matches(self, model: FileMatcherModel) -> bool:
        self._registry.append(model)
        return self._constant_result

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        self._registry.append(model)
        return self._new_tb().build_result(self._constant_result)
