import pathlib
import unittest

from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.file_matcher import FileMatcherSdv
from exactly_lib.symbol.logic.logic_type_sdv import MatcherTypeSdv
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.matcher.impls import combinator_matchers
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib_test.test_case_utils.file_matcher.test_resources import file_matcher_models as models
from exactly_lib_test.test_case_utils.test_resources import matcher_combinators_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestAnd),
        unittest.makeSuite(TestOr),
        unittest.makeSuite(TestNot),
    ])


class FileMatcherConfiguration(matcher_combinators_check.MatcherConfiguration[FileMatcherModel]):
    def mk_logic_type(self, generic: MatcherSdv[FileMatcherModel]) -> MatcherTypeSdv[FileMatcherModel]:
        return FileMatcherSdv(generic)

    def logic_type(self) -> LogicValueType:
        return LogicValueType.FILE_MATCHER

    def parser(self) -> Parser[MatcherTypeSdv[FileMatcherModel]]:
        return parse_file_matcher.parser()

    def irrelevant_model(self) -> FileMatcherModel:
        return models.new_model(pathlib.Path('irrelevant path'))


class TestAnd(matcher_combinators_check.TestAndBase[FileMatcherModel]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> matcher_combinators_check.MatcherConfiguration[FileMatcherModel]:
        return FileMatcherConfiguration()

    def new_combinator_to_check(self, constructor_argument) -> MatcherWTrace[FileMatcherModel]:
        return combinator_matchers.Conjunction(constructor_argument)


class TestOr(matcher_combinators_check.TestOrBase[FileMatcherModel]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> matcher_combinators_check.MatcherConfiguration[FileMatcherModel]:
        return FileMatcherConfiguration()

    def new_combinator_to_check(self, constructor_argument) -> MatcherWTrace[FileMatcherModel]:
        return combinator_matchers.Disjunction(constructor_argument)


class TestNot(matcher_combinators_check.TestNotBase[FileMatcherModel]):
    # To debug an individual test case - override the test method in the super class
    # and call super.
    @property
    def configuration(self) -> matcher_combinators_check.MatcherConfiguration[FileMatcherModel]:
        return FileMatcherConfiguration()

    def new_combinator_to_check(self, constructor_argument) -> MatcherWTrace[FileMatcherModel]:
        return combinator_matchers.Negation(constructor_argument)
