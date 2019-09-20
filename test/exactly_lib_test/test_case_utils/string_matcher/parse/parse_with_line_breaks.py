import unittest
from typing import Optional

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.type_system.err_msg.error_message import ErrorMessageResolver
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.arguments_building import SB
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.misc import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.test_configuration import \
    TestCaseBase
from exactly_lib_test.test_case_utils.string_matcher.test_resources import model_construction
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import is_arbitrary_matching_failure, \
    is_matching_success, Expectation
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestLineBreaksWithEmptyActualFile(),
    ])


class Case:
    def __init__(self,
                 name: str,
                 source: ParseSource,
                 source_assertion: ValueAssertion[ParseSource],
                 main_result_assertion: ValueAssertion[Optional[ErrorMessageResolver]],
                 ):
        self.name = name
        self.source = source
        self.source_assertion = source_assertion
        self.main_result_assertion = main_result_assertion


class TestLineBreaksWithEmptyActualFile(TestCaseBase):
    def runTest(self):
        sb = SB.new_with(constant_transformation_arguments=argument_syntax.syntax_for_transformer_option(
            argument_syntax.syntax_for_replace_transformer('a', 'A')
        ))

        cases = [
            Case('CONTENTS-MATCHER on separate line',
                 source=
                 self.configuration.source_for_lines(
                     sb.format_lines(['',
                                      '{empty}'])),
                 source_assertion=
                 asrt_source.is_at_end_of_line(2),
                 main_result_assertion=
                 is_matching_success(),
                 ),
            Case('transformation and CONTENTS-MATCHER on separate line',
                 source=
                 self.configuration.source_for_lines(
                     sb.format_lines(['',
                                      '{constant_transformation_arguments}',
                                      '{empty}'])),
                 source_assertion=
                 asrt_source.is_at_end_of_line(3),
                 main_result_assertion=
                 is_matching_success(),
                 ),
            Case('negation and CONTENTS-MATCHER on separate line',
                 source=
                 self.configuration.source_for_lines(
                     sb.format_lines(['',
                                      '{not}',
                                      '{empty}'])),
                 source_assertion=
                 asrt_source.is_at_end_of_line(3),
                 main_result_assertion=
                 is_arbitrary_matching_failure(),
                 ),
        ]
        for case in cases:
            with self.subTest(case.name):
                self._check(
                    case.source,
                    model_construction.empty_model(),
                    self.configuration.arrangement_for_contents(
                        post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY),
                    Expectation(
                        main_result=case.main_result_assertion,
                        source=case.source_assertion
                    ),
                )
