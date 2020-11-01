import unittest
from abc import ABC, abstractmethod

from exactly_lib.instructions.multi_phase.define_symbol import parser as sut
from exactly_lib.symbol.value_type import LogicValueType
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib_test.instructions.multi_phase.define_symbol.test_resources.source_formatting import src3
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import \
    InstructionApplicationEnvironment
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.symbol.test_resources.types import LOGIC_VALUE_TYPE_2_VALUE_TYPE
from exactly_lib_test.test_resources import matcher_argument
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase, \
    MessageBuilder
from exactly_lib_test.type_val_deps.logic.test_resources.matcher_symbol_context import MatcherTypeSymbolContext
from exactly_lib_test.type_val_deps.sym_ref.test_resources.container_assertions import matches_container_of_logic_type
from exactly_lib_test.type_val_deps.types.test_resources import matcher_sdv_type_assertions


class AssertApplicationOfMatcherInSymbolTable(ValueAssertionBase[InstructionApplicationEnvironment], ABC):
    def __init__(self,
                 matcher_symbol_name: str,
                 expected_matcher_result: ValueAssertion[MatchingResult]):
        self.matcher_symbol_name = matcher_symbol_name
        self.expected_matcher_result = expected_matcher_result

    def _apply(self,
               put: unittest.TestCase,
               value: InstructionApplicationEnvironment,
               message_builder: MessageBuilder):
        result = self._apply_matcher(value)

        self.expected_matcher_result.apply_with_message(put, result, 'matching result')

    @abstractmethod
    def _apply_matcher(self, environment: InstructionApplicationEnvironment) -> MatchingResult:
        pass


def check_matcher_should_be_parsed_as_full_expression(put: unittest.TestCase,
                                                      symbol_1: MatcherTypeSymbolContext,
                                                      symbol_2: MatcherTypeSymbolContext,
                                                      logic_value_type: LogicValueType,
                                                      ):
    # ARRANGE #
    symbols = [symbol_1, symbol_2]

    value_argument = matcher_argument.disjunction([symbol_1.argument, symbol_2.argument])

    defined_name = 'the_defined_name'

    source = remaining_source(
        src3(LOGIC_VALUE_TYPE_2_VALUE_TYPE[logic_value_type],
             defined_name,
             value_argument.as_str,
             ),
    )

    # EXPECTATION #

    expected_symbol_references = SymbolContext.references_assertion_of_contexts(symbols)

    expected_container = matches_container_of_logic_type(
        logic_value_type,
        matcher_sdv_type_assertions.matches_sdv_of_file_matcher(
            references=expected_symbol_references,
            primitive_value=asrt.anything_goes(),
            symbols=SymbolContext.symbol_table_of_contexts(symbols)
        )
    )
    expected_symbol_usages = asrt.matches_singleton_sequence(
        asrt_sym_usage.matches_definition(asrt.equals(defined_name), expected_container)
    )

    expected_source = asrt_source.source_is_at_end

    # ACT #

    actual = sut.PARTS_PARSER.parse(ARBITRARY_FS_LOCATION_INFO, source)

    # ASSERT #

    expected_source.apply_with_message(put, source, 'source')
    expected_symbol_usages.apply_with_message(put, actual.symbol_usages, 'symbol usages')
