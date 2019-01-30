import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher as sut
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.file_matcher.test_resources.model_construction import ModelConstructor
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__for_expression_parser
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    expectation_type_config__non_is_success, ExpectationTypeConfigForNoneIsSuccess


class TestCaseBase(unittest.TestCase):
    def _check(self,
               source: ParseSource,
               model: ModelConstructor,
               arrangement: ArrangementPostAct,
               expectation: Expectation):
        integration_check.check(self,
                                sut.parser(),
                                source,
                                model,
                                arrangement,
                                expectation)

    def _check_with_source_variants(self,
                                    arguments: Arguments,
                                    model: ModelConstructor,
                                    arrangement: ArrangementPostAct,
                                    expectation: Expectation):
        for source in equivalent_source_variants__with_source_check__for_expression_parser(self, arguments):
            integration_check.check(self,
                                    sut.parser(),
                                    source,
                                    model,
                                    arrangement,
                                    expectation)


class TestWithNegationArgumentBase(TestCaseBase):
    def runTest(self):
        for expectation_type in ExpectationType:
            with self.subTest(expectation_type=expectation_type):
                self._doTest(expectation_type_config__non_is_success(expectation_type))

    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        raise NotImplementedError('abstract method')
