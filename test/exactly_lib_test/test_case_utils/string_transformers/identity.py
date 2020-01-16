import unittest

from exactly_lib.test_case_utils.string_transformer import names
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.string_transformers.test_resources import integration_check
from exactly_lib_test.test_case_utils.string_transformers.test_resources import model_assertions as asrt_model
from exactly_lib_test.test_case_utils.string_transformers.test_resources import model_construction
from exactly_lib_test.test_case_utils.string_transformers.test_resources.integration_check import Arrangement, \
    Expectation
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        Test(),
    ])


class Test(integration_check.TestCaseWithCheckMethods):
    def runTest(self):
        # ARRANGE #
        arguments = names.IDENTITY_TRANSFORMER_NAME

        model_content_lines = ['the model contents line 1']

        # ACT & ASSERT #

        self._check_with_source_variants(
            Arguments(arguments),
            model_construction.of_lines(model_content_lines),
            Arrangement(),
            Expectation(
                main_result=asrt_model.model_as_list_matches(asrt.equals(model_content_lines)),
                is_identity_transformer=asrt.equals(True)
            )
        )
