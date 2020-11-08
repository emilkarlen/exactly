import unittest
from typing import List

from exactly_lib.impls.types.string_transformer import names
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ParseExpectation, \
    ExecutionExpectation, Expectation, prim_asrt__constant
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.impls.types.string_model.test_resources import model_constructor
from exactly_lib_test.impls.types.string_transformers.test_resources import integration_check, \
    may_dep_on_ext_resources
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_prims.string_model.test_resources import assertions as asrt_string_model
from exactly_lib_test.type_val_prims.string_transformer.test_resources.string_transformer_assertions import \
    is_identity_transformer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        Test(),
        TestMayDependOnExternalResourcesShouldBeThatOfSourceModel(),
    ])


class TestMayDependOnExternalResourcesShouldBeThatOfSourceModel(
    may_dep_on_ext_resources.TestMayDepOnExtResourcesShouldBeThatOfSourceModelBase):
    def argument_cases(self) -> List[str]:
        return [names.IDENTITY_TRANSFORMER_NAME]

    def is_identity_transformer(self) -> bool:
        return True


class Test(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        arguments = names.IDENTITY_TRANSFORMER_NAME

        model_content_lines = ['the model contents line 1']

        # ACT & ASSERT #

        integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
            self,
            Arguments(arguments),
            model_constructor.of_lines(self, model_content_lines),
            arrangement_w_tcds(),
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.is_empty_sequence,
                ),
                ExecutionExpectation(
                    main_result=asrt_string_model.model_lines_lists_matches(
                        asrt.equals(model_content_lines),
                        may_depend_on_external_resources=asrt.equals(False),
                    )
                ),
                prim_asrt__constant(is_identity_transformer(True))
            )
        )
