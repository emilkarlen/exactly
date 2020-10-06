import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.string_matcher import parse_string_matcher as sut
from exactly_lib.test_case_utils.string_transformer import names
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.logic.test_resources.string_transformer.assertions import \
    is_reference_to_string_transformer
from exactly_lib_test.symbol.logic.test_resources.string_transformer.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.symbol.test_resources.string_matcher import StringMatcherSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import Arrangement, arrangement_w_tcds, \
    ParseExpectation, ExecutionExpectation, PrimAndExeExpectation, Expectation
from exactly_lib_test.test_case_utils.string_matcher.test_resources import contents_transformation, integration_check, \
    arguments_building2 as args2
from exactly_lib_test.test_case_utils.string_matcher.test_resources import string_matchers
from exactly_lib_test.test_case_utils.string_matcher.test_resources import \
    validation_cases as string_matcher_failing_validation_cases
from exactly_lib_test.test_case_utils.string_models.test_resources import model_constructor
from exactly_lib_test.test_case_utils.string_transformers.test_resources import validation_cases \
    as string_transformer_failing_validation_cases
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_resources.test_utils import NExArr, NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_transformer.test_resources import string_transformers
from exactly_lib_test.type_system.logic.string_transformer.test_resources.string_transformers import \
    delete_everything
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes_str


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestStringTransformerShouldBeParsedAsSimpleExpression(),
        TestStringMatcherShouldBeParsedAsSimpleExpression(),
        TestValidationShouldFailWhenValidationOfStringMatcherFails(),
        TestValidationShouldFailWhenValidationOfStringTransformerFails(),
        TestWhenStringTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents(),
        unittest.makeSuite(TestWithBinaryOperators),
    ])


_TRANSFORMER_SYMBOL_NAME = 'the_transformer'


class TestWhenStringTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        original_model_contents = 'some text'
        expected_model_contents = original_model_contents.upper()

        cases = [
            NEA(
                'transformation that makes matcher match',
                True,
                string_transformers.to_uppercase(),
            ),
            NEA(
                'transformation that makes matcher NOT match',
                False,
                delete_everything(),
            ),
        ]

        # ACT & ASSERT #

        integration_check.CHECKER__PARSE_FULL.check_multi__w_source_variants(
            self,
            args2.Transformed(
                _TRANSFORMER_SYMBOL_NAME,
                args2.Equals(surrounded_by_hard_quotes_str(expected_model_contents))
            ).as_arguments,
            asrt.matches_singleton_sequence(
                is_reference_to_string_transformer(_TRANSFORMER_SYMBOL_NAME)
            ),
            model_constructor.of_str(self, original_model_contents),
            [
                NExArr(
                    case.name,
                    PrimAndExeExpectation.of_exe(
                        main_result=asrt_matching_result.matches_value(case.expected),
                    ),
                    arrangement_w_tcds(
                        symbols=StringTransformerSymbolContext.of_primitive(_TRANSFORMER_SYMBOL_NAME, case.actual
                                                                            ).symbol_table,
                    )
                )
                for case in cases
            ],
        )


class TestStringTransformerShouldBeParsedAsSimpleExpression(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        string_transformer_argument = ab.binary_operator(
            names.SEQUENCE_OPERATOR_NAME,
            [
                ab.symbol_reference('TRANSFORMER_SYMBOL_1'),
                ab.symbol_reference('TRANSFORMER_SYMBOL_2'),
            ],
        )
        arguments = args2.Transformed(
            str(string_transformer_argument),
            args2.SymbolReferenceWReferenceSyntax('STRING_MATCHER_SYMBOL')
        )
        cases = [
            NameAndValue(
                'parse STRING-MATCHER as simple expr',
                sut.parsers().simple,
            ),
            NameAndValue(
                'parse STRING-MATCHER as full expr',
                sut.parsers().full,
            ),
        ]

        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    case.value.parse(arguments.as_remaining_source)


class TestStringMatcherShouldBeParsedAsSimpleExpression(unittest.TestCase):
    def runTest(self):
        model__original = 'the model text'
        the_model_constructor = model_constructor.of_str(self, model__original)

        string_transformer = StringTransformerSymbolContext.of_primitive(
            'THE_STRING_TRANSFORMER',
            string_transformers.to_uppercase()
        )
        sm_equals = StringMatcherSymbolContext.of_primitive(
            'STRING_MATCHER_1',
            string_matchers.EqualsConstant(model__original.upper())
        )
        symbol = [
            string_transformer,
            sm_equals,
        ]

        after_bin_op = 'after bin op'
        sm_conjunction = args2.conjunction([
            args2.SymbolReference(sm_equals.name),
            args2.Custom(after_bin_op),
        ])
        arguments = args2.Transformed(
            string_transformer.name__sym_ref_syntax,
            sm_conjunction
        )
        integration_check.CHECKER__PARSE_SIMPLE.check(
            self,
            source=arguments.as_remaining_source,
            input_=the_model_constructor,
            arrangement=arrangement_w_tcds(
                symbols=SymbolContext.symbol_table_of_contexts(symbol),
            ),
            expectation=Expectation(
                ParseExpectation(
                    source=asrt_source.is_at_line(
                        current_line_number=1,
                        remaining_part_of_current_line=' '.join([sm_conjunction.operator, after_bin_op])
                    ),
                    symbol_references=SymbolContext.references_assertion_of_contexts(symbol)
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(True)
                )
            ),
        )


class TestValidationShouldFailWhenValidationOfStringMatcherFails(unittest.TestCase):
    def runTest(self):
        string_transformer = StringTransformerSymbolContext.of_primitive(
            'the_string_transformer',
            string_transformers.arbitrary()
        )
        for case in string_matcher_failing_validation_cases.failing_validation_cases():
            with self.subTest(validation_case=case.name):
                symbol_context = case.value.symbol_context
                integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
                    self,
                    args2.Transformed(
                        string_transformer.name,
                        args2.SymbolReference(symbol_context.name)
                    ).as_arguments,
                    model_constructor.must_not_be_used,
                    Arrangement(
                        symbols=SymbolContext.symbol_table_of_contexts([
                            string_transformer,
                            symbol_context,
                        ])
                    ),
                    Expectation(
                        ParseExpectation(
                            symbol_references=asrt.matches_sequence([
                                string_transformer.reference_assertion,
                                symbol_context.reference_assertion,
                            ]),
                        ),
                        ExecutionExpectation(
                            validation=case.value.expectation,
                        ),
                    ),
                )


class TestValidationShouldFailWhenValidationOfStringTransformerFails(unittest.TestCase):
    def runTest(self):
        for case in string_transformer_failing_validation_cases.failing_validation_cases():
            with self.subTest(validation_case=case.name):
                integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
                    self,
                    args2.Transformed(
                        case.value.symbol_context.name,
                        args2.Empty()
                    ).as_arguments,
                    model_constructor.must_not_be_used,
                    Arrangement(
                        symbols=case.value.symbol_context.symbol_table
                    ),
                    Expectation(
                        ParseExpectation(
                            symbol_references=case.value.symbol_context.references_assertion,
                        ),
                        ExecutionExpectation(
                            validation=case.value.expectation,
                        ),
                    ),
                )


class TestWithBinaryOperators(unittest.TestCase):
    def test_transformation_SHOULD_apply_to_all_operands_if_matcher_is_binary_operator_expression(self):
        to_upper_transformer = StringTransformerSymbolContext.of_primitive(
            'the_to_upper_transformer',
            string_transformers.to_uppercase()
        )

        model = contents_transformation.TransformedContentsSetup(
            original='text',
            transformed='TEXT',
        )

        integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
            self,
            args2.Transformed(
                to_upper_transformer.name,
                args2.Parenthesis(
                    args2.conjunction([
                        args2.Equals(model.transformed),
                        args2.Equals(model.original),
                    ])
                )
            ).as_arguments,
            model_constructor.of_str(self, model.original),
            arrangement_w_tcds(
                symbols=to_upper_transformer.symbol_table
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_singleton_sequence(
                        to_upper_transformer.reference_assertion
                    )
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(False)
                )
            )
        )

    def test_transformation_SHOULD_apply_only_to_matcher_argument(self):
        to_upper_transformer = StringTransformerSymbolContext.of_primitive(
            'the_to_upper_transformer',
            string_transformers.to_uppercase()
        )

        model = contents_transformation.TransformedContentsSetup(
            original='text',
            transformed='TEXT',
        )

        integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
            self,
            args2.conjunction([
                args2.Parenthesis(
                    args2.Transformed(
                        to_upper_transformer.name,
                        args2.Equals(model.transformed)
                    ),
                ),
                args2.Equals(model.original),
            ]).as_arguments,
            model_constructor.of_str(self, model.original),
            arrangement_w_tcds(
                symbols=to_upper_transformer.symbol_table
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_singleton_sequence(
                        is_reference_to_string_transformer(to_upper_transformer.name)
                    )
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(True)
                )
            )
        )

    def test_tree_of_transformations(self):
        # ARRANGE #

        to_upper_transformer = StringTransformerSymbolContext.of_primitive(
            'the_to_upper_transformer',
            string_transformers.to_uppercase()
        )

        keep_line_1 = StringTransformerSymbolContext.of_primitive(
            'keep_line_1',
            string_transformers.keep_single_line(1)
        )

        keep_line_2 = StringTransformerSymbolContext.of_primitive(
            'keep_line_2',
            string_transformers.keep_single_line(2)
        )

        equals_1st = StringMatcherSymbolContext.of_primitive(
            'equals_1st',
            string_matchers.EqualsConstant('1ST\n')
        )

        equals_2nd = StringMatcherSymbolContext.of_primitive(
            'equals_2nd',
            string_matchers.EqualsConstant('2ND\n')
        )

        model__original = '1st\n2nd\n'

        symbol_contexts = [
            to_upper_transformer,
            keep_line_1,
            equals_1st,
            keep_line_2,
            equals_2nd,
        ]

        # ACT & ASSERT #

        integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
            self,
            args2.Transformed(
                to_upper_transformer.name__sym_ref_syntax,
                args2.Parenthesis(
                    args2.conjunction([
                        args2.Parenthesis(
                            args2.Transformed(keep_line_1.name__sym_ref_syntax,
                                              args2.SymbolReference(equals_1st.name),
                                              )
                        ),
                        args2.Parenthesis(
                            args2.Transformed(keep_line_2.name__sym_ref_syntax,
                                              args2.SymbolReference(equals_2nd.name),
                                              )
                        ),
                    ])
                )
            ).as_arguments,
            model_constructor.of_str(self, model__original),
            arrangement_w_tcds(
                symbols=SymbolContext.symbol_table_of_contexts(symbol_contexts)
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=SymbolContext.references_assertion_of_contexts(symbol_contexts)
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(True)
                )
            )
        )
