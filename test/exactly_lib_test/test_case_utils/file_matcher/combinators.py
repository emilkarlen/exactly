import pathlib
import unittest

from exactly_lib.test_case_utils.file_matcher import file_matchers as sut
from exactly_lib.test_case_utils.file_matcher.impl import combinators
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib_test.test_case_utils.file_matcher.test_resources import file_matcher_models as model
from exactly_lib_test.test_case_utils.file_matcher.test_resources.file_matchers import FileMatcherConstantWithName
from exactly_lib_test.test_case_utils.test_resources import matcher_combinators_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestAnd),
        unittest.makeSuite(TestOr),
        unittest.makeSuite(TestNot),
    ])


class FileMatcherConfiguration(matcher_combinators_check.MatcherConfiguration):
    def irrelevant_model(self) -> FileMatcherModel:
        return model.with_dir_space_that_must_not_be_used(pathlib.Path('irrelevant path'))

    def matcher_with_constant_result(self,
                                     name: str,
                                     result: bool):
        return FileMatcherConstantWithName(name, result)

    def matcher_that_registers_model_argument_and_returns_constant(
            self, result: bool
    ) -> matcher_combinators_check.MatcherThatRegistersModelArgument:
        return FileMatcherThatRegistersModelArgument(result)


class TestAnd(matcher_combinators_check.TestAndBase):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> matcher_combinators_check.MatcherConfiguration:
        return FileMatcherConfiguration()

    def new_combinator_to_check(self, constructor_argument):
        return combinators.FileMatcherAnd(constructor_argument)


class TestOr(matcher_combinators_check.TestOrBase):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> matcher_combinators_check.MatcherConfiguration:
        return FileMatcherConfiguration()

    def new_combinator_to_check(self, constructor_argument):
        return combinators.FileMatcherOr(constructor_argument)


class TestNot(matcher_combinators_check.TestNotBase):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> matcher_combinators_check.MatcherConfiguration:
        return FileMatcherConfiguration()

    def new_combinator_to_check(self, constructor_argument):
        return combinators.FileMatcherNot(constructor_argument)


class FileMatcherThatRegistersModelArgument(sut.FileMatcherImplBase,
                                            matcher_combinators_check.MatcherThatRegistersModelArgument):

    @property
    def name(self) -> str:
        return str(type(self))

    @property
    def option_description(self) -> str:
        raise NotImplementedError('this method should not be used')

    def matches(self, model: FileMatcherModel) -> bool:
        self.register_argument(model)
        return self._constant_result
