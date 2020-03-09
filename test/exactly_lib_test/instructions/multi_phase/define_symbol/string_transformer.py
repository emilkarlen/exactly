import unittest

from exactly_lib.instructions.multi_phase import define_symbol as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.string_transformer.names import REPLACE_TRANSFORMER_NAME, SEQUENCE_OPERATOR_NAME
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.instructions.multi_phase.define_symbol.test_case_base import TestCaseBaseForParser
from exactly_lib_test.instructions.multi_phase.define_symbol.test_resources import *
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.sdv_structure_assertions import matches_container, is_sdtv_of_logic_type
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer__ref, \
    StringTransformerSymbolContext
from exactly_lib_test.symbol.test_resources.symbol_syntax import NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case_utils.parse.test_resources.source_case import SourceCase
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax
from exactly_lib_test.test_case_utils.string_transformers.test_resources import assertions as asrt_sdv
from exactly_lib_test.test_case_utils.string_transformers.test_resources import transformers
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources import string_transformer_assertions as asrt_string_transformer
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulScenarios),
        unittest.makeSuite(TestUnsuccessfulScenarios),
    ])


class TestSuccessfulScenarios(TestCaseBaseForParser):
    def test_successful_parse_of_sequence(self):
        # ARRANGE #

        regex_str = 'the_regex'
        replacement_str = 'the_replacement'

        symbol = StringTransformerSymbolContext.of_primitive(
            'the_symbol_name',
            transformers.StringTransformerThatMustNotBeUsedTestImpl()
        )

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
            SourceCase('Expression on following line',
                       source=
                       remaining_source(
                           src('{lines_trans_type} {defined_name} = {new_line} {transformer_argument}',
                               defined_name=defined_name,
                               transformer_argument=argument_syntax.syntax_for_sequence_of_transformers([
                                   symbol.name,
                                   replace_transformer_syntax,
                               ])),
                           following_lines=['following line'],
                       ),
                       source_assertion=asrt_source.is_at_beginning_of_line(3)
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

        expected_container = matches_container(
            assertion_on_sdv=is_sdtv_of_logic_type(
                LogicValueType.STRING_TRANSFORMER,
                asrt_sdv.resolved_value_matches_string_transformer(
                    asrt_string_transformer.is_identity_transformer(False),
                    references=asrt.matches_sequence([
                        is_reference_to_string_transformer__ref(symbol.name),
                    ]),
                    symbols=symbol.symbol_table,
                )
            ))

        for source_case in cases:
            with self.subTest(source_case.name):
                expectation = Expectation(
                    symbol_usages=asrt.matches_sequence([
                        asrt_sym_usage.matches_definition(asrt.equals(defined_name),
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
            NameAndValue(
                'single quoted argument',
                str(surrounded_by_hard_quotes(REPLACE_TRANSFORMER_NAME)),
            ),
            NameAndValue(
                'non-transformer name that is not a valid symbol name',
                NOT_A_VALID_SYMBOL_NAME,
            ),
            NameAndValue(
                'missing transformer',
                '',
            ),
        ]
        # ARRANGE #
        defined_name = 'defined_name'
        parser = sut.EmbryoParser()
        for case in cases:
            with self.subTest(name=case.name):
                source = single_line_source(
                    src('{lines_trans_type} {defined_name} = {transformer_argument}',
                        defined_name=defined_name,
                        transformer_argument=case.value),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    # ACT & ASSERT #
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
