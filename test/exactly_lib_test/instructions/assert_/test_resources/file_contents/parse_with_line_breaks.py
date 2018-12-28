import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.result import pfh
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfiguration, TestWithConfigurationBase
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.test_case.result.test_resources import pfh_assertions
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.arguments_building import SB
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite_for(configuration: InstructionTestConfiguration) -> unittest.TestSuite:
    test_cases = [
        TestLineBreaksWithEmptyActualFile,
    ]
    return unittest.TestSuite(
        [tc(configuration) for tc in test_cases])


class Case:
    def __init__(self,
                 name: str,
                 source: ParseSource,
                 source_assertion: ValueAssertion[ParseSource],
                 main_result_assertion: ValueAssertion[pfh.PassOrFailOrHardError],
                 ):
        self.name = name
        self.source = source
        self.source_assertion = source_assertion
        self.main_result_assertion = main_result_assertion


class TestLineBreaksWithEmptyActualFile(TestWithConfigurationBase):
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
                 asrt_source.source_is_at_end,
                 main_result_assertion=
                 pfh_assertions.is_pass(),
                 ),
            Case('transformation and CONTENTS-MATCHER on separate line',
                 source=
                 self.configuration.source_for_lines(
                     sb.format_lines(['',
                                      '{constant_transformation_arguments}',
                                      '{empty}'])),
                 source_assertion=
                 asrt_source.source_is_at_end,
                 main_result_assertion=
                 pfh_assertions.is_pass(),
                 ),
            Case('negation and CONTENTS-MATCHER on separate line',
                 source=
                 self.configuration.source_for_lines(
                     sb.format_lines(['',
                                      '{not}',
                                      '{empty}'])),
                 source_assertion=
                 asrt_source.source_is_at_end,
                 main_result_assertion=
                 pfh_assertions.is_fail(),
                 ),
        ]
        for case in cases:
            with self.subTest(case.name):
                self._check(
                    case.source,
                    self.configuration.arrangement_for_contents(
                        actual_contents='',
                        post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY),
                    Expectation(main_result=case.main_result_assertion,
                                source=case.source_assertion),
                )
