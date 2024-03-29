import unittest
from typing import List

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Arrangement, Expectation
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_expression_parser
from exactly_lib_test.impls.types.string_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.string_source.test_resources.model_constructor import ModelConstructor
from exactly_lib_test.impls.types.test_resources.negation_argument_handling import \
    expectation_type_config__non_is_success, ExpectationTypeConfigForNoneIsSuccess
from exactly_lib_test.test_resources.arguments.arguments_building import Arguments


def arguments_for(additional_arguments: str, following_lines=()) -> Arguments:
    return Arguments(additional_arguments, following_lines)


def source_for_lines(argument_lines: List[str]) -> ParseSource:
    return source_for(argument_lines[0], argument_lines[1:])


def source_for(argument_tail: str, following_lines=()) -> ParseSource:
    return arguments_for(argument_tail).followed_by_lines(following_lines).as_remaining_source


class TestCaseBase(unittest.TestCase):
    def _check(self,
               source: ParseSource,
               model: ModelConstructor,
               arrangement: Arrangement,
               expectation: Expectation):
        integration_check.CHECKER__PARSE_FULL.check(self,
                                                    source,
                                                    model,
                                                    arrangement,
                                                    expectation)

    def _check_with_source_variants(self,
                                    instruction_argument: Arguments,
                                    model: ModelConstructor,
                                    arrangement: Arrangement,
                                    expectation: Expectation):
        for source in equivalent_source_variants__for_expression_parser(
                self, instruction_argument):
            integration_check.CHECKER__PARSE_FULL.check(self,
                                                        source,
                                                        model,
                                                        arrangement,
                                                        expectation,
                                                        )


class TestWithNegationArgumentBase(TestCaseBase):
    def runTest(self):
        for expectation_type in ExpectationType:
            with self.subTest(expectation_type=expectation_type):
                self._doTest(expectation_type_config__non_is_success(expectation_type))

    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        raise NotImplementedError('abstract method')
