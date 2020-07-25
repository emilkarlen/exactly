from typing import List, Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib_test.test_case_utils.logic.test_resources import integration_check as logic_integration_check
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import Expectation, ParseExpectation, \
    ExecutionExpectation, prim_asrt__constant
from exactly_lib_test.test_case_utils.string_transformers.test_resources.model_assertions import \
    model_lines_lists_matches
from exactly_lib_test.test_case_utils.string_transformers.test_resources.transformer_checker import \
    StringTransformerPropertiesConfiguration
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.string_transformer.test_resources import \
    string_transformer_assertions as asrt_string_transformer

StExpectation = Expectation[StringTransformer, StringModel]

CHECKER = logic_integration_check.IntegrationChecker(
    parse_string_transformer.parser(),
    StringTransformerPropertiesConfiguration()
)


def expectation_of_successful_execution(output_lines: List[str],
                                        symbol_references: ValueAssertion[Sequence[SymbolReference]],
                                        is_identity_transformer: bool = False) -> StExpectation:
    return Expectation(
        ParseExpectation(
            symbol_references=symbol_references
        ),
        ExecutionExpectation(
            main_result=model_lines_lists_matches(asrt.equals(output_lines))
        ),
        prim_asrt__constant(
            asrt_string_transformer.is_identity_transformer(is_identity_transformer)
        )
    )
