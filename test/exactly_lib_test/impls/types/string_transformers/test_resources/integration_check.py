from typing import List, Sequence

from exactly_lib.impls.types.string_transformer import parse_string_transformer
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib_test.impls.types.logic.test_resources import integration_check as logic_integration_check
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Expectation, ParseExpectation, \
    ExecutionExpectation, prim_asrt__constant
from exactly_lib_test.impls.types.string_transformers.test_resources.transformer_checker import \
    StringTransformerPropertiesConfiguration
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source
from exactly_lib_test.type_val_prims.string_transformer.test_resources import \
    string_transformer_assertions as asrt_string_transformer

StExpectation = Expectation[StringTransformer, StringSource]

CHECKER__PARSE_FULL = logic_integration_check.IntegrationChecker(
    parse_string_transformer.parsers(True).full,
    StringTransformerPropertiesConfiguration(avoid_model_evaluation=False),
    True,
)

CHECKER__PARSE_SIMPLE = logic_integration_check.IntegrationChecker(
    parse_string_transformer.parsers(True).simple,
    StringTransformerPropertiesConfiguration(avoid_model_evaluation=False),
    True,
)

CHECKER__PARSE_SIMPLE__WO_IMPLICIT_MODEL_EVALUATION = logic_integration_check.IntegrationChecker(
    parse_string_transformer.parsers(True).simple,
    StringTransformerPropertiesConfiguration(avoid_model_evaluation=True),
    True,
)


def expectation_of_successful_execution(output_lines: List[str],
                                        may_depend_on_external_resources: bool,
                                        symbol_references: ValueAssertion[Sequence[SymbolReference]],
                                        is_identity_transformer: bool = False,
                                        source: ValueAssertion[ParseSource] = asrt.anything_goes()) -> StExpectation:
    return Expectation(
        ParseExpectation(
            source=source,
            symbol_references=symbol_references
        ),
        ExecutionExpectation(
            main_result=asrt_string_source.matches__lines(
                asrt.equals(output_lines),
                may_depend_on_external_resources=asrt.equals(may_depend_on_external_resources),
            ),
        ),
        prim_asrt__constant(
            asrt_string_transformer.is_identity_transformer(is_identity_transformer)
        )
    )
