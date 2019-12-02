import unittest
from typing import Sequence

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher as sut
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.file_matcher.test_resources import model_construction
from exactly_lib_test.test_case_utils.file_matcher.test_resources.model_construction import ModelConstructor
from exactly_lib_test.test_case_utils.file_matcher.test_resources.test_utils import Actual
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__for_expression_parser
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import expectation
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    expectation_type_config__non_is_success, ExpectationTypeConfigForNoneIsSuccess
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.type_system.data.test_resources import described_path
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result


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

    def _assert_failing_parse(self, source: ParseSource):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parser().parse(source)

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

    def _check_cases__with_source_variants(self, cases: Sequence[NEA[bool, Actual]]):
        for case in cases:
            with self.subTest(case_name=case.name,
                              regex=case.actual.arguments):
                self._check_with_source_variants(
                    arguments=
                    case.actual.arguments,
                    model=
                    model_construction.constant_model(described_path.new_primitive(case.actual.path)),
                    arrangement=ArrangementPostAct(),
                    expectation=expectation(
                        main_result=asrt_matching_result.matches_value(case.expected)
                    )
                )


class TestWithNegationArgumentBase(TestCaseBase):
    def runTest(self):
        for expectation_type in ExpectationType:
            with self.subTest(expectation_type=expectation_type):
                self._doTest(expectation_type_config__non_is_success(expectation_type))

    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        raise NotImplementedError('abstract method')
