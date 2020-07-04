import unittest

from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.test_resources.program import NON_EXISTING_SYSTEM_PROGRAM
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as args
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import ParseExpectation, Expectation, \
    ExecutionExpectation, arrangement_w_tcds
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as program_args


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestHardError()
    ])


class TestHardError(unittest.TestCase):
    def runTest(self):
        # ARRANGE & ACT && ASSERT #
        integration_check.CHECKER.check(
            self,
            args.RunProgram(
                program_args.system_program_argument_elements(NON_EXISTING_SYSTEM_PROGRAM)
            ).as_remaining_source,
            integration_check.ARBITRARY_MODEL,
            arrangement_w_tcds(),
            Expectation(
                ParseExpectation(
                    source=asrt_source.source_is_at_end,
                ),
                ExecutionExpectation(
                    is_hard_error=asrt_text_doc.is_any_text()
                ),
            ),
        )
