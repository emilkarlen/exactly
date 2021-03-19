import unittest

from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ParseExpectation, \
    ExecutionExpectation, Expectation
from exactly_lib_test.impls.types.program.test_resources import arguments_building as program_args
from exactly_lib_test.impls.types.string_matcher.test_resources import arguments_building2 as args
from exactly_lib_test.impls.types.string_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.string_source.test_resources import model_constructor
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import NON_EXISTING_SYSTEM_PROGRAM


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestHardError()
    ])


class TestHardError(unittest.TestCase):
    def runTest(self):
        # ARRANGE & ACT && ASSERT #
        integration_check.CHECKER__PARSE_FULL.check(
            self,
            args.RunProgram(
                program_args.system_program_argument_elements(NON_EXISTING_SYSTEM_PROGRAM)
            ).as_remaining_source,
            model_constructor.arbitrary(self),
            arrangement_w_tcds(),
            Expectation(
                ParseExpectation(
                    source=asrt_source.is_at_end_of_line(1),
                ),
                ExecutionExpectation(
                    is_hard_error=asrt_text_doc.is_any_text()
                ),
            ),
        )
