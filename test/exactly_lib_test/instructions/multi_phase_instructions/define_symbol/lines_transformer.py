import unittest

from exactly_lib.instructions.multi_phase_instructions import define_symbol as sut
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.lines_transformer.parse_lines_transformer import REPLACE_TRANSFORMER_NAME, \
    SEQUENCE_OPERATOR_NAME
from exactly_lib.test_case_utils.lines_transformer.resolvers import LinesTransformerConstant
from exactly_lib.type_system.logic.lines_transformer import IdentityLinesTransformer, SequenceLinesTransformer
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.multi_phase_instructions.define_symbol.test_case_base import TestCaseBaseForParser
from exactly_lib_test.instructions.multi_phase_instructions.define_symbol.test_resources import *
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.test_resources import resolver_structure_assertions as asrt_ne
from exactly_lib_test.symbol.test_resources.lines_transformer import is_lines_transformer_reference_to
from exactly_lib_test.symbol.test_resources.resolver_structure_assertions import matches_container
from exactly_lib_test.symbol.test_resources.symbol_syntax import NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_utils.lines_transformers import parse_lines_transformer
from exactly_lib_test.test_case_utils.lines_transformers.test_resources import argument_syntax
from exactly_lib_test.test_case_utils.lines_transformers.test_resources.resolver_assertions import \
    resolved_value_equals_lines_transformer
from exactly_lib_test.test_case_utils.parse.test_resources.source_case import SourceCase
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulScenarios),
        unittest.makeSuite(TestUnsuccessfulScenarios),
    ])


class TestSuccessfulScenarios(TestCaseBaseForParser):
    def test_successful_parse_WHEN_rhs_is_empty_THEN_result_SHOULD_be_identity_transformer(self):
        defined_name = 'defined_name'

        # ARRANGE #

        source = single_line_source(
            src('{lines_trans_type} {defined_name} = ',
                defined_name=defined_name),
        )

        # EXPECTATION #

        expected_container = matches_container(
            resolved_value_equals_lines_transformer(IdentityLinesTransformer())
        )

        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                asrt_ne.matches_definition(asrt.equals(defined_name),
                                           expected_container)
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                defined_name,
                expected_container,
            )
        )

        # ACT & ASSERT #

        self._check(source, ArrangementWithSds(), expectation)

    def test_successful_parse_of_sequence(self):
        # ARRANGE #

        regex_str = 'the_regex'
        replacement_str = 'the_replacement'

        symbol = NameAndValue('the_symbol_name',
                              parse_lines_transformer.CustomLinesTransformerTestImpl())

        replace_transformer_syntax = argument_syntax.syntax_for_replace_transformer(regex_str,
                                                                                    replacement_str)

        defined_name = 'defined_name'

        cases = [
            SourceCase('Expression on single line',
                       source=
                       remaining_source(
                           src('{lines_trans_type} {defined_name} = {transformer_argument}',
                               defined_name=defined_name,
                               transformer_argument=argument_syntax.syntax_for_sequence_of_transformers([
                                   symbol.name,
                                   replace_transformer_syntax,
                               ])),
                           following_lines=['following line'],
                       ),
                       source_assertion=asrt_source.is_at_beginning_of_line(2)
                       ),
            SourceCase('1st expr on first line followed by operator, 2nd expr on next line',
                       source=
                       remaining_source(
                           src('{lines_trans_type} {defined_name} = {symbol_name} {sequence_operator}',
                               defined_name=defined_name,
                               symbol_name=symbol.name,
                               sequence_operator=SEQUENCE_OPERATOR_NAME),
                           following_lines=[replace_transformer_syntax],
                       ),
                       source_assertion=asrt_source.source_is_at_end
                       ),
            SourceCase('1st expr on first line followed by operator, 2nd expr on next line, non-exr on 3rd line',
                       source=
                       remaining_source(
                           src('{lines_trans_type} {defined_name} = {symbol_name} {sequence_operator}',
                               defined_name=defined_name,
                               symbol_name=symbol.name,
                               sequence_operator=SEQUENCE_OPERATOR_NAME),
                           following_lines=[replace_transformer_syntax,
                                            'following line'],
                       ),
                       source_assertion=asrt_source.is_at_beginning_of_line(3)
                       ),
        ]
        # EXPECTATION #

        the_sequence_transformer = SequenceLinesTransformer([
            symbol.value,
            parse_lines_transformer.replace_transformer(regex_str,
                                                        replacement_str),
        ])

        expected_container = matches_container(
            assertion_on_resolver=
            resolved_value_equals_lines_transformer(
                the_sequence_transformer,
                references=asrt.matches_sequence([
                    is_lines_transformer_reference_to(symbol.name),
                ]),
                symbols=SymbolTable({
                    symbol.name: container(LinesTransformerConstant(symbol.value)),
                }),
            )
        )

        for source_case in cases:
            with self.subTest(source_case.name):
                expectation = Expectation(
                    symbol_usages=asrt.matches_sequence([
                        asrt_ne.matches_definition(asrt.equals(defined_name),
                                                   expected_container)
                    ]),
                    symbols_after_main=assert_symbol_table_is_singleton(
                        defined_name,
                        expected_container,
                    ),
                    source=source_case.source_assertion
                )

                # ACT & ASSERT #

                self._check(source_case.source, ArrangementWithSds(), expectation)


class TestUnsuccessfulScenarios(TestCaseBaseForParser):
    def test_failing_parse(self):
        cases = [
            (
                'single quoted argument',
                str(surrounded_by_hard_quotes(REPLACE_TRANSFORMER_NAME)),
            ),
            (
                'non-transformer name that is not a valid symbol name',
                NOT_A_VALID_SYMBOL_NAME,
            ),
        ]
        # ARRANGE #
        defined_name = 'defined_name'
        parser = sut.EmbryoParser()
        for name, rhs_source in cases:
            with self.subTest(name=name):
                source = single_line_source(
                    src('{lines_trans_type} {defined_name} = {transformer_argument}',
                        defined_name=defined_name,
                        transformer_argument=rhs_source),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    # ACT & ASSERT #
                    parser.parse(source)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
