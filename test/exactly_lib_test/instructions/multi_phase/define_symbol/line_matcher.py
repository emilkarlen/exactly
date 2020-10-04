import unittest

from exactly_lib.definitions.primitives import line_matcher
from exactly_lib.instructions.multi_phase.define_symbol import parser as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.test_case_utils.matcher.impls import sdv_components, constant
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.instructions.multi_phase.define_symbol.test_resources import matcher_helpers
from exactly_lib_test.instructions.multi_phase.define_symbol.test_resources.embryo_checker import INSTRUCTION_CHECKER
from exactly_lib_test.instructions.multi_phase.define_symbol.test_resources.source_formatting import *
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.symbol.logic.test_resources.resolving_helper import resolving_helper
from exactly_lib_test.symbol.test_resources import sdv_type_assertions
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.container_assertions import matches_container_of_logic_type
from exactly_lib_test.symbol.test_resources.line_matcher import LineMatcherSymbolContext, \
    is_reference_to_line_matcher
from exactly_lib_test.symbol.test_resources.symbol_syntax import NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case_utils.line_matcher.test_resources import argument_syntax
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources import matcher_assertions as asrt_matcher
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulScenarios),
        unittest.makeSuite(TestUnsuccessfulScenarios),
    ])


class TestSuccessfulScenarios(unittest.TestCase):
    def test_successful_parse_of_regex(self):
        # ARRANGE #

        regex_str = 'the_regex'
        models_for_equivalence_check = [
            asrt_matcher.ModelInfo((1, regex_str)),
            asrt_matcher.ModelInfo((2, 'before' + regex_str + 'after')),
            asrt_matcher.ModelInfo((1, 'no match')),
        ]

        symbol = LineMatcherSymbolContext.of_sdv(
            'the_symbol_name',
            CONSTANT_TRUE_MATCHER_SDV)

        regex_matcher_syntax = argument_syntax.syntax_for_regex_matcher(regex_str)

        matcher_argument = argument_syntax.syntax_for_and([
            symbol.name,
            regex_matcher_syntax,
        ])

        defined_name = 'defined_name'

        argument_cases = [
            NameAndValue('value on same line',
                         '{matcher_argument}'
                         ),
            NameAndValue('value on following line',
                         '{new_line} {matcher_argument}'
                         ),
        ]

        for argument_case in argument_cases:
            with self.subTest(argument_case.name):
                source = remaining_source(
                    src2(ValueType.LINE_MATCHER, defined_name, argument_case.value,
                         matcher_argument=matcher_argument),
                    following_lines=['following line'],
                )

                # EXPECTATION #

                symbol_table = symbol.symbol_table

                expected_matcher_sdv = parse_line_matcher.parsers().full.parse(remaining_source(matcher_argument))

                expected_matcher = resolving_helper(symbol_table).resolve_matcher(expected_matcher_sdv)

                expected_container = matches_container_of_logic_type(
                    LogicValueType.LINE_MATCHER,
                    sdv=sdv_type_assertions.matches_sdv_of_line_matcher(
                        references=asrt.matches_sequence([
                            is_reference_to_line_matcher(symbol.name),
                        ]),
                        primitive_value=asrt_matcher.is_equivalent_to(expected_matcher,
                                                                      models_for_equivalence_check),
                        symbols=symbol_table,
                    )
                )

                expectation = Expectation(
                    symbol_usages=asrt.matches_sequence([
                        asrt_sym_usage.matches_definition(asrt.equals(defined_name),
                                                          expected_container)
                    ]),
                    symbols_after_main=assert_symbol_table_is_singleton(
                        defined_name,
                        expected_container,
                    )
                )

                # ACT & ASSERT #

                INSTRUCTION_CHECKER.check(self, source, ArrangementWithSds(), expectation)

    def test_matcher_SHOULD_be_parsed_as_full_expression(self):
        matcher_helpers.check_matcher_should_be_parsed_as_full_expression(
            self,
            LineMatcherSymbolContext.of_arbitrary_value('symbol_1'),
            LineMatcherSymbolContext.of_arbitrary_value('symbol_2'),
            LogicValueType.LINE_MATCHER,
        )


class TestUnsuccessfulScenarios(unittest.TestCase):
    def test_failing_parse(self):
        cases = [
            NameAndValue(
                'single quoted argument',
                str(surrounded_by_hard_quotes(line_matcher.CONTENTS_MATCHER_NAME)),
            ),
            NameAndValue(
                'non-transformer name that is not a valid symbol name',
                NOT_A_VALID_SYMBOL_NAME,
            ),
            NameAndValue(
                'missing matcher',
                '',
            ),
        ]
        # ARRANGE #
        parser = sut.EmbryoParser()
        for case in cases:
            with self.subTest(name=case.name):
                source = single_line_source(
                    src2(ValueType.LINE_MATCHER, 'defined_name', case.value),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    # ACT & ASSERT #
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


CONSTANT_TRUE_MATCHER_SDV = sdv_components.matcher_sdv_from_constant_primitive(
    constant.MatcherWithConstantResult(True)
)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
