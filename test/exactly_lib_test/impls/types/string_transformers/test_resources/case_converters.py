import unittest
from abc import ABC, abstractmethod
from typing import Callable

from exactly_lib.util.str_.misc_formatting import with_appended_new_lines
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.impls.types.string_model.test_resources import model_constructor
from exactly_lib_test.impls.types.string_transformers.test_resources import integration_check
from exactly_lib_test.impls.types.string_transformers.test_resources.integration_check import \
    expectation_of_successful_execution
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class CaseConverterConfig:
    def __init__(self,
                 arguments: str,
                 str_transformer: Callable[[str], str],
                 ):
        self.arguments = arguments
        self.str_transformer = str_transformer


class CaseConverterTestBase(unittest.TestCase, ABC):
    @property
    @abstractmethod
    def config(self) -> CaseConverterConfig:
        pass

    def test_no_lines(self):
        integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
            self,
            Arguments(self.config.arguments),
            model_constructor.of_lines(self, []),
            arrangement_w_tcds(),
            expectation_of_successful_execution(
                symbol_references=asrt.is_empty_sequence,
                output_lines=[],
                may_depend_on_external_resources=False,
                is_identity_transformer=False,
            )
        )

    def test_every_line_SHOULD_be_transformed(self):
        # ARRANGE #
        trans_fun = self.config.str_transformer
        input_lines = [
            'I object!',
            'Object Oriented',
            'Unidentified FLYING Object',
        ]
        expected_lines = [
            trans_fun(line)
            for line in input_lines
        ]
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
            self,
            Arguments(self.config.arguments),
            model_constructor.of_lines_wo_nl(self, input_lines),
            arrangement_w_tcds(),
            expectation_of_successful_execution(
                symbol_references=asrt.is_empty_sequence,
                output_lines=with_appended_new_lines(expected_lines),
                may_depend_on_external_resources=False,
                is_identity_transformer=False,
            )
        )
