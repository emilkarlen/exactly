from abc import ABC

from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_case_utils.file_matcher.names.test_resources import configuration
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.file_matcher.test_resources import parse_check
from exactly_lib_test.test_case_utils.file_matcher.test_resources.argument_building import NameGlobPatternVariant, \
    NameRegexVariant
from exactly_lib_test.test_case_utils.file_matcher.test_resources.integration_check import ARBITRARY_MODEL
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ParseExpectation, \
    ExecutionExpectation, Expectation, arrangement_wo_tcds
from exactly_lib_test.test_case_utils.regex.test_resources.assertions import is_regex_reference_restrictions
from exactly_lib_test.test_case_utils.regex.test_resources.validation_cases import failing_regex_validation_cases
from exactly_lib_test.test_case_utils.test_resources import glob_pattern
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.matcher_argument import NameRegexComponent
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringSymbolContext


class TestSyntax(configuration.TestCaseBase, ABC):
    def test_glob_pattern(self):
        def make_arguments(pattern: str) -> ArgumentElementsRenderer:
            return self.conf.arguments(
                NameGlobPatternVariant(pattern)
            )

        parse_check.PARSE_CHECKER__SIMPLE.check_invalid_syntax_cases_for_expected_valid_token(
            self,
            make_arguments,
        )

    def test_regex(self):
        for ignore_case in [False, True]:
            with self.subTest(ignore_case=ignore_case):
                def make_arguments(pattern: str) -> ArgumentElementsRenderer:
                    return self.conf.arguments(
                        NameRegexVariant(NameRegexComponent(pattern, ignore_case))
                    )

                parse_check.PARSE_CHECKER__SIMPLE.check_invalid_syntax_cases_for_expected_valid_token(
                    self,
                    make_arguments,
                )


class TestValidation(configuration.TestCaseBase, ABC):
    def test_validation_should_fail_pre_sds_when_regex_is_invalid(self):
        for regex_case in failing_regex_validation_cases():
            arguments = self.conf.arguments(NameRegexVariant.of(regex_case.regex_string))
            for expectation_type in ExpectationType:
                with self.subTest(expectation_type=expectation_type,
                                  validation_case=regex_case.case_name):
                    integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants(
                        self,
                        arguments=
                        arguments.as_arguments,
                        input_=
                        ARBITRARY_MODEL,
                        arrangement=
                        arrangement_w_tcds(
                            symbols=SymbolContext.symbol_table_of_contexts(regex_case.symbols)
                        ),
                        expectation=
                        Expectation(
                            ParseExpectation(
                                symbol_references=asrt.matches_sequence(regex_case.reference_assertions),
                            ),
                            ExecutionExpectation(
                                validation=regex_case.expectation
                            ),
                        )
                    )


class TestSymbolReferences(configuration.TestCaseBase, ABC):
    def test_glob_pattern(self):
        match_anything_glob_pattern_string_symbol = StringSymbolContext.of_constant(
            'glob_pattern_symbol',
            '*',
            default_restrictions=glob_pattern.is_glob_pattern_string_reference_restrictions()
        )
        arguments = self.conf.arguments(
            NameGlobPatternVariant(match_anything_glob_pattern_string_symbol.name__sym_ref_syntax)
        )

        integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants(
            self,
            arguments=
            arguments.as_arguments,
            input_=
            ARBITRARY_MODEL,
            arrangement=arrangement_wo_tcds(
                symbols=match_anything_glob_pattern_string_symbol.symbol_table
            ),
            expectation=Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_sequence([
                        match_anything_glob_pattern_string_symbol.reference_assertion,
                    ]),
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value__w_header(
                        asrt.equals(True),
                        asrt.equals(self.conf.node_name)
                    )
                ),
            )
        )

    def test_reg_ex(self):
        match_anything_regex_string_symbol = StringSymbolContext.of_constant(
            'regex_symbol',
            '.*',
            default_restrictions=is_regex_reference_restrictions()
        )
        arguments = self.conf.arguments(
            NameRegexVariant.of(match_anything_regex_string_symbol.name__sym_ref_syntax)
        )

        integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants(
            self,
            arguments=
            arguments.as_arguments,
            input_=
            ARBITRARY_MODEL,
            arrangement=arrangement_wo_tcds(
                symbols=match_anything_regex_string_symbol.symbol_table
            ),
            expectation=Expectation(
                ParseExpectation(
                    symbol_references=match_anything_regex_string_symbol.references_assertion,
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value__w_header(
                        asrt.equals(True),
                        asrt.equals(self.conf.node_name)
                    )
                ),
            )
        )
