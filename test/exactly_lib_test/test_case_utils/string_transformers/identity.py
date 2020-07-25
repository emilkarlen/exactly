import unittest

from exactly_lib.test_case_utils.string_transformer import names
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ParseExpectation, \
    ExecutionExpectation, Expectation, prim_asrt__constant
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.string_transformers.test_resources import integration_check
from exactly_lib_test.test_case_utils.string_transformers.test_resources import model_assertions as asrt_model
from exactly_lib_test.test_case_utils.string_transformers.test_resources import model_construction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_transformer.test_resources.string_transformer_assertions import \
    is_identity_transformer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        Test(),
    ])


class Test(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        arguments = names.IDENTITY_TRANSFORMER_NAME

        model_content_lines = ['the model contents line 1']

        # ACT & ASSERT #

        integration_check.CHECKER.check__w_source_variants(
            self,
            Arguments(arguments),
            model_construction.of_lines(model_content_lines),
            arrangement_w_tcds(),
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.is_empty_sequence,
                ),
                ExecutionExpectation(
                    main_result=asrt_model.model_lines_lists_matches(asrt.equals(model_content_lines))
                ),
                prim_asrt__constant(is_identity_transformer(True))
            )
        )
