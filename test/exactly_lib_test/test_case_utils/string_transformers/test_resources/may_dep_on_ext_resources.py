import unittest
from abc import ABC, abstractmethod
from typing import List

from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, Expectation, \
    ParseExpectation, ExecutionExpectation, prim_asrt__constant
from exactly_lib_test.test_case_utils.string_models.test_resources import model_constructor
from exactly_lib_test.test_case_utils.string_models.test_resources.model_constructor import ModelConstructor
from exactly_lib_test.test_case_utils.string_transformers.test_resources import integration_check
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_prims.string_model.test_resources.assertions import model_lines_lists_matches
from exactly_lib_test.type_val_prims.string_transformer.test_resources import \
    string_transformer_assertions as asrt_string_transformer


class TestMayDepOnExtResourcesShouldBeThatOfSourceModelBase(unittest.TestCase, ABC):
    @abstractmethod
    def argument_cases(self) -> List[str]:
        pass

    def expected_output_lines_for_model(self) -> ValueAssertion[List[str]]:
        return asrt.equals([])

    def model(self,
              may_depend_on_external_resources: bool,
              ) -> ModelConstructor:
        return model_constructor.empty(self,
                                       may_depend_on_external_resources=may_depend_on_external_resources)

    def is_identity_transformer(self) -> bool:
        return False

    def runTest(self):
        # ARRANGE #
        for arguments in self.argument_cases():
            for may_depend_on_external_resources in [False, True]:
                with self.subTest(may_depend_on_external_resources=may_depend_on_external_resources,
                                  arguments=repr(arguments)):
                    # ACT & ASSERT #
                    integration_check.CHECKER__PARSE_SIMPLE.check(
                        self,
                        remaining_source(arguments),
                        self.model(may_depend_on_external_resources),
                        arrangement_w_tcds(),
                        Expectation(
                            ParseExpectation(
                                symbol_references=asrt.is_empty_sequence
                            ),
                            ExecutionExpectation(
                                main_result=model_lines_lists_matches(
                                    self.expected_output_lines_for_model(),
                                    may_depend_on_external_resources=asrt.equals(may_depend_on_external_resources),
                                ),
                            ),
                            prim_asrt__constant(
                                asrt_string_transformer.is_identity_transformer(
                                    self.is_identity_transformer()
                                )
                            )
                        ),
                    )
