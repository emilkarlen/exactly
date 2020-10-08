import unittest
from abc import ABC, abstractmethod
from typing import List

from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import arrangement_w_tcds
from exactly_lib_test.test_case_utils.string_models.test_resources import model_constructor
from exactly_lib_test.test_case_utils.string_transformers.test_resources import integration_check
from exactly_lib_test.test_case_utils.string_transformers.test_resources.integration_check import \
    expectation_of_successful_execution
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class TestMayDepOnExtResourcesShouldBeThatOfSourceModelBase(unittest.TestCase, ABC):
    @abstractmethod
    def argument_cases(self) -> List[str]:
        pass

    def expected_output_lines_for_empty_model(self) -> List[str]:
        return []

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
                        model_constructor.empty(self,
                                                may_depend_on_external_resources=may_depend_on_external_resources),
                        arrangement_w_tcds(),
                        expectation_of_successful_execution(
                            symbol_references=asrt.is_empty_sequence,
                            output_lines=self.expected_output_lines_for_empty_model(),
                            may_depend_on_external_resources=may_depend_on_external_resources,
                            is_identity_transformer=self.is_identity_transformer(),
                        )
                    )
