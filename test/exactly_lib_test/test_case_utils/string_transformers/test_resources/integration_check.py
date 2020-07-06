from typing import List, Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerModel
from exactly_lib_test.test_case_utils.logic.test_resources import integration_check as logic_integration_check
from exactly_lib_test.test_case_utils.string_transformers.test_resources.model_assertions import model_as_list_matches
from exactly_lib_test.test_case_utils.string_transformers.test_resources.transformer_checker import \
    StringTransformerPropertiesConfiguration
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.string_transformer.test_resources import \
    string_transformer_assertions as asrt_string_transformer

StExpectation = logic_integration_check.Expectation[StringTransformer, StringTransformerModel]

CHECKER = logic_integration_check.IntegrationChecker(
    parse_string_transformer.parser(),
    StringTransformerPropertiesConfiguration()
)


def expectation_of_successful_execution(output_lines: List[str],
                                        symbol_references: ValueAssertion[Sequence[SymbolReference]],
                                        is_identity_transformer: bool = False) -> StExpectation:
    return logic_integration_check.Expectation(
        logic_integration_check.ParseExpectation(
            symbol_references=symbol_references
        ),
        logic_integration_check.ExecutionExpectation(
            main_result=model_as_list_matches(asrt.equals(output_lines))
        ),
        asrt_string_transformer.is_identity_transformer(is_identity_transformer),
    )
