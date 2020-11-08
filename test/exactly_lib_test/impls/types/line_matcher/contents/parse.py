import unittest

from exactly_lib.definitions import logic
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import line_matcher
from exactly_lib.type_val_prims.string_model import StringModel
from exactly_lib.util.description_tree import tree
from exactly_lib_test.impls.types.file_matcher.test_resources import parse_test_base_classes as tc
from exactly_lib_test.impls.types.line_matcher.test_resources import arguments_building as lm_args
from exactly_lib_test.impls.types.line_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.line_matcher.test_resources import models
from exactly_lib_test.impls.types.line_matcher.test_resources import parse_check
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ParseExpectation, \
    ExecutionExpectation, Expectation, arrangement_wo_tcds
from exactly_lib_test.impls.types.matcher.test_resources.assertion_applier import MatcherThatAppliesValueAssertion
from exactly_lib_test.impls.types.matcher.test_resources.matchers import ConstantMatcherWithCustomTrace, T
from exactly_lib_test.impls.types.string_matcher.test_resources import arguments_building2 as sm_args2
from exactly_lib_test.impls.types.string_matcher.test_resources import validation_cases
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.test_resources import argument_renderer
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.test_resources.string_matcher import \
    StringMatcherSymbolContextOfPrimitiveConstant, \
    StringMatcherSymbolContext
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions as asrt_d_tree, \
    rendering_assertions as asrt_trace_rendering

MATCHER_NAME = ' '.join((line_matcher.CONTENTS_MATCHER_NAME,
                         syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT.singular_name))

TRACE_HEADER_EXPECTATION = asrt.equals(MATCHER_NAME)


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestInvalidSyntax(),
        StringMatcherShouldBeValidated(),
        TestResultShouldBeResultOfStringMatcher(),
        TestModelOfAppliedStringMatcherShouldBeLineModelContents(),
        TestStringMatcherShouldBeParsedAsSimpleExpression(),
        TestTrace(),
    ])


class TestInvalidSyntax(unittest.TestCase):
    def runTest(self):
        def make_arguments(matcher_argument: str) -> ArgumentElementsRenderer:
            return lm_args.Contents(
                argument_renderer.Singleton(matcher_argument)
            )

        parse_check.PARSE_CHECKER__SIMPLE.check_invalid_syntax_cases_for_expected_valid_token(
            self,
            make_arguments,
        )


class TestStringMatcherShouldBeParsedAsSimpleExpression(unittest.TestCase):
    def runTest(self):
        string_matcher = StringMatcherSymbolContextOfPrimitiveConstant(
            'STRING_MATCHER',
            True,
        )
        after_bin_op = 'after bin op'
        integration_check.CHECKER__PARSE_SIMPLE.check(
            self,
            source=lm_args.Contents(
                sm_args2.conjunction([
                    sm_args2.SymbolReference(string_matcher.name),
                    sm_args2.Custom(after_bin_op),
                ]),
            ).as_remaining_source,
            input_=models.ARBITRARY_MODEL,
            arrangement=arrangement_wo_tcds(
                symbols=string_matcher.symbol_table,
            ),
            expectation=Expectation(
                ParseExpectation(
                    source=asrt_source.is_at_line(
                        current_line_number=1,
                        remaining_part_of_current_line=logic.AND_OPERATOR_NAME + ' ' + after_bin_op),
                    symbol_references=string_matcher.references_assertion
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value__w_header(
                        asrt.equals(string_matcher.result_value),
                        header=TRACE_HEADER_EXPECTATION,
                    )
                )
            ),
        )


class TestResultShouldBeResultOfStringMatcher(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        for result in [False, True]:
            string_matcher = StringMatcherSymbolContextOfPrimitiveConstant(
                'STRING_MATCHER',
                result,
            )
            # ACT & ASSERT #
            with self.subTest(string_matcher_result=result):
                integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants(
                    self,
                    arguments=lm_args.Contents(
                        sm_args2.SymbolReferenceWReferenceSyntax(string_matcher.name),
                    ).as_arguments,
                    input_=models.ARBITRARY_MODEL,
                    arrangement=arrangement_wo_tcds(
                        symbols=string_matcher.symbol_table,
                    ),
                    expectation=Expectation(
                        ParseExpectation(
                            symbol_references=string_matcher.references_assertion
                        ),
                        ExecutionExpectation(
                            main_result=asrt_matching_result.matches_value__w_header(
                                asrt.equals(string_matcher.result_value),
                                header=TRACE_HEADER_EXPECTATION,
                            )
                        )
                    ),
                )


class TestTrace(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        def get_trace(data: T) -> tree.Node[T]:
            return tree.Node.empty('name of string matcher', data)

        for string_matcher_result in [False, True]:
            string_matcher = StringMatcherSymbolContext.of_primitive(
                'STRING_MATCHER',
                ConstantMatcherWithCustomTrace(
                    get_trace,
                    string_matcher_result
                ),
            )
            expected_trace = tree.Node(
                MATCHER_NAME,
                string_matcher_result,
                (),
                [get_trace(string_matcher_result)],
            )

            # ACT & ASSERT #
            with self.subTest(string_matcher_result=string_matcher_result):
                integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants(
                    self,
                    arguments=lm_args.Contents(
                        sm_args2.SymbolReferenceWReferenceSyntax(string_matcher.name),
                    ).as_arguments,
                    input_=models.ARBITRARY_MODEL,
                    arrangement=arrangement_wo_tcds(
                        symbols=string_matcher.symbol_table,
                    ),
                    expectation=Expectation(
                        ParseExpectation(
                            symbol_references=string_matcher.references_assertion
                        ),
                        ExecutionExpectation(
                            main_result=asrt_matching_result.matches(
                                asrt.equals(string_matcher_result),
                                trace=asrt_trace_rendering.matches_node_renderer(
                                    asrt_d_tree.equals_node(expected_trace)
                                ),
                            )
                        )
                    ),
                )


class TestModelOfAppliedStringMatcherShouldBeLineModelContents(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        line_contents = 'the line contents'

        def get_string_matcher_model_as_single_string(model: StringModel) -> str:
            return model.as_str

        matching_result = True
        string_matcher = StringMatcherSymbolContext.of_primitive(
            'STRING_MATCHER',
            MatcherThatAppliesValueAssertion(
                self,
                assertion=asrt.equals(line_contents),
                get_actual=get_string_matcher_model_as_single_string,
                message_builder=asrt.MessageBuilder.new('string-matcher-model'),
                matching_result=matching_result,
            ),
        )
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants(
            self,
            arguments=lm_args.Contents(
                sm_args2.SymbolReferenceWReferenceSyntax(string_matcher.name),
            ).as_arguments,
            input_=models.constant((1, line_contents)),
            arrangement=arrangement_wo_tcds(
                symbols=string_matcher.symbol_table,
            ),
            expectation=Expectation(
                ParseExpectation(
                    symbol_references=string_matcher.references_assertion
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value__w_header(
                        asrt.equals(matching_result),
                        header=asrt.equals(MATCHER_NAME),
                    )
                )
            ),
        )


class StringMatcherShouldBeValidated(tc.TestCaseBase):
    def runTest(self):
        for case in validation_cases.failing_validation_cases():
            symbol_context = case.value.symbol_context
            with self.subTest(case.name):
                integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants(
                    self,
                    arguments=
                    lm_args.Contents(
                        sm_args2.SymbolReferenceWReferenceSyntax(symbol_context.name)
                    ).as_arguments,
                    input_=
                    models.ARBITRARY_MODEL,
                    arrangement=
                    arrangement_w_tcds(
                        symbols=symbol_context.symbol_table,
                    ),
                    expectation=
                    Expectation(
                        ParseExpectation(
                            symbol_references=symbol_context.references_assertion,
                        ),
                        ExecutionExpectation(
                            validation=case.value.expectation,
                        ),
                    ),
                )
