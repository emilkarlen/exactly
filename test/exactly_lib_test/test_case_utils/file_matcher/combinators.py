import pathlib
import unittest

from exactly_lib.test_case_utils.file_matcher import file_matchers as sut
from exactly_lib_test.test_case_utils.test_resources import combinator_matcher_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestAnd),
        unittest.makeSuite(TestOr),
        unittest.makeSuite(TestNot),
    ])


class FileMatcherConfiguration(combinator_matcher_check.MatcherConfiguration):
    def irrelevant_model(self):
        return pathlib.Path('irrelevant path')

    def matcher_with_constant_result(self, result: bool):
        return sut.FileMatcherConstant(result)

    def apply(self, matcher_to_check, model) -> bool:
        assert isinstance(matcher_to_check, sut.FileMatcher)  # Sanity check
        return matcher_to_check.matches(model)

    def matcher_that_registers_model_argument_and_returns_constant(
            self, result: bool
    ) -> combinator_matcher_check.MatcherThatRegistersModelArgument:
        return FileMatcherThatRegistersModelArgument(result)


class TestAnd(combinator_matcher_check.TestAndBase):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> combinator_matcher_check.MatcherConfiguration:
        return FileMatcherConfiguration()

    def new_combinator_to_check(self, constructor_argument):
        return sut.FileMatcherAnd(constructor_argument)


class TestOr(combinator_matcher_check.TestOrBase):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> combinator_matcher_check.MatcherConfiguration:
        return FileMatcherConfiguration()

    def new_combinator_to_check(self, constructor_argument):
        return sut.FileMatcherOr(constructor_argument)


class TestNot(combinator_matcher_check.TestNotBase):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> combinator_matcher_check.MatcherConfiguration:
        return FileMatcherConfiguration()

    def new_combinator_to_check(self, constructor_argument):
        return sut.FileMatcherNot(constructor_argument)


class FileMatcherThatRegistersModelArgument(sut.FileMatcher,
                                            combinator_matcher_check.MatcherThatRegistersModelArgument):
    @property
    def option_description(self) -> str:
        raise NotImplementedError('this method should not be used')

    def select_from(self, directory: pathlib.Path) -> iter:
        raise NotImplementedError('this method should not be used')

    def matches(self, line: str) -> bool:
        self.register_argument(line)
        return self._constant_result
