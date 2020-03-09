import unittest
from typing import List

from exactly_lib.definitions import logic
from exactly_lib.definitions.test_case import file_check_properties
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_file_structure.path_relativity import RelNonHdsOptionType
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer__ref, \
    StringTransformerSymbolContext
from exactly_lib_test.test_case_file_structure.test_resources import non_hds_populator
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import NonHdsPopulator
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_syntax, integration_check
from exactly_lib_test.test_case_utils.file_matcher.test_resources import parse_test_base_classes as tc
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import arrangement_w_tcds, Expectation, \
    ExecutionExpectation, ParseExpectation
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments, elements
from exactly_lib_test.test_case_utils.string_matcher.test_resources import validation_cases
from exactly_lib_test.test_case_utils.string_matcher.test_resources.arguments_building import args as sm_args, \
    EqualsStringAssertionArgumentsConstructor
from exactly_lib_test.test_case_utils.test_resources import matcher_assertions
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForNoneIsSuccess
from exactly_lib_test.test_resources.files.file_structure import empty_file, File, DirContents, empty_dir, \
    FileSystemElement
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_transformer.test_resources import EveryLineEmptyStringTransformer
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes_str


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestHardErrorWhenActualFileDoesNotExist(),
        TestHardErrorWhenActualFileIsADirectory(),
        EmbeddedStringMatcherShouldBeValidated(),
        ActualFileIsEmpty(),
        ActualFileIsEmptyAfterTransformation(),
        TestComplexMatcher(),
        TestComplexMatcherWithParenthesis(),
        TestEvaluationIsLazyFromLeftToRight(),
    ])


def arguments_for(additional_arguments: str, following_lines=()) -> Arguments:
    return Arguments(file_check_properties.REGULAR_FILE_CONTENTS + ' ' + additional_arguments,
                     following_lines)


def source_for_lines(argument_lines: List[str]) -> ParseSource:
    return source_for(argument_lines[0], argument_lines[1:])


def source_for(argument_tail: str, following_lines=()) -> ParseSource:
    return arguments_for(argument_tail).followed_by_lines(following_lines).as_remaining_source


def single_file_in_current_dir(f: FileSystemElement) -> NonHdsPopulator:
    return non_hds_populator.rel_option(
        RelNonHdsOptionType.REL_ACT,
        DirContents([f])
    )


class EmbeddedStringMatcherShouldBeValidated(tc.TestCaseBase):
    def runTest(self):
        for case in validation_cases.failing_validation_cases():
            symbol_context = case.value.symbol_context
            symbols = symbol_context.symbol_table

            with self.subTest(case.name):
                self._check(
                    source=
                    source_for(
                        sm_args(symbol_context.name)
                    ),
                    model_constructor=
                    integration_check.constant_relative_file_name('non-existing.txt'),
                    arrangement=
                    arrangement_w_tcds(
                        symbols=symbols,
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


class TestHardErrorWhenActualFileDoesNotExist(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        self._check(
            source=
            source_for(
                sm_args('{maybe_not} {empty}',
                        maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
            model_constructor=
            integration_check.constant_relative_file_name('non-existing.txt'),
            arrangement=
            arrangement_w_tcds(),
            expectation=
            Expectation(
                execution=ExecutionExpectation(
                    is_hard_error=asrt.anything_goes()
                ),
            ),
        )


class TestHardErrorWhenActualFileIsADirectory(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        checked_file = empty_dir('a-dir')

        self._check(
            source=
            source_for(
                sm_args('{maybe_not} {empty}',
                        maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
            model_constructor=
            integration_check.constant_relative_file_name(checked_file.name),
            arrangement=
            arrangement_w_tcds(
                non_hds_contents=single_file_in_current_dir(checked_file)
            ),
            expectation=
            Expectation(
                execution=ExecutionExpectation(
                    is_hard_error=asrt.anything_goes()
                ),
            ),
        )


class ActualFileIsEmpty(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        checked_file = empty_file('actual.txt')

        self._check_with_source_variants(
            arguments=
            arguments_for(
                sm_args('{maybe_not} {empty}',
                        maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
            model_constructor=
            integration_check.constant_relative_file_name(checked_file.name),
            arrangement=
            arrangement_w_tcds(
                non_hds_contents=single_file_in_current_dir(checked_file)
            ),
            expectation=
            Expectation(
                execution=ExecutionExpectation(
                    main_result=maybe_not.pass__if_positive__fail__if_negative
                )
            ),
        )


class ActualFileIsEmptyAfterTransformation(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        # ARRANGE #

        named_transformer = StringTransformerSymbolContext.of_primitive('the_transformer',
                                                                        EveryLineEmptyStringTransformer())

        checked_file = File('actual.txt', 'some\ntext')

        symbols = named_transformer.symbol_table

        expected_symbol_reference_to_transformer = is_reference_to_string_transformer__ref(named_transformer.name)

        expected_symbol_usages = asrt.matches_sequence([expected_symbol_reference_to_transformer])

        # ACT & ASSERT #

        self._check_with_source_variants(
            arguments=
            arguments_for(
                sm_args('{transform_option} {the_transformer} {maybe_not} {empty}',
                        the_transformer=named_transformer.name,
                        maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
            model_constructor=
            integration_check.constant_relative_file_name(checked_file.name),
            arrangement=
            arrangement_w_tcds(
                non_hds_contents=single_file_in_current_dir(checked_file),
                symbols=symbols,
            ),
            expectation=
            Expectation(
                ParseExpectation(
                    symbol_references=expected_symbol_usages
                ),
                ExecutionExpectation(
                    main_result=maybe_not.pass__if_positive__fail__if_negative,
                ),
            )
        )


class TestComplexMatcher(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        checked_file = File('actual.txt', 'file contents')

        self._check(
            source=
            elements(
                maybe_not.empty__if_positive__not_option__if_negative +
                [
                    '(',
                    argument_syntax.contents_matcher_of(
                        str(EqualsStringAssertionArgumentsConstructor(
                            surrounded_by_hard_quotes_str(checked_file.contents)))),
                    ')',
                    logic.AND_OPERATOR_NAME,
                    argument_syntax.name_glob_pattern_matcher_of(checked_file.name),
                ]
            ).as_remaining_source,
            model_constructor=
            integration_check.constant_relative_file_name(checked_file.name),
            arrangement=
            arrangement_w_tcds(
                non_hds_contents=single_file_in_current_dir(checked_file)
            ),
            expectation=
            Expectation(
                execution=ExecutionExpectation(
                    main_result=maybe_not.pass__if_positive__fail__if_negative
                ),
            ),
        )


class TestComplexMatcherWithParenthesis(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        checked_file = File('actual.txt', 'file contents')

        self._check(
            source=
            elements(
                maybe_not.empty__if_positive__not_option__if_negative +
                [
                    '(',
                    argument_syntax.contents_matcher_of(
                        str(EqualsStringAssertionArgumentsConstructor(
                            surrounded_by_hard_quotes_str(checked_file.contents)))),
                    ')',
                    logic.AND_OPERATOR_NAME,
                    argument_syntax.name_glob_pattern_matcher_of(checked_file.name),
                ]
            ).as_remaining_source,
            model_constructor=
            integration_check.constant_relative_file_name(checked_file.name),
            arrangement=
            arrangement_w_tcds(
                non_hds_contents=single_file_in_current_dir(checked_file)
            ),
            expectation=
            Expectation(
                execution=ExecutionExpectation(
                    main_result=maybe_not.pass__if_positive__fail__if_negative
                ),
            ),
        )


class TestEvaluationIsLazyFromLeftToRight(tc.TestCaseBase):
    def runTest(self):
        checked_file = empty_dir('a-dir')

        self._check(
            source=
            elements(
                [
                    argument_syntax.type_matcher_of(FileType.REGULAR),
                    logic.AND_OPERATOR_NAME,
                    argument_syntax.contents_matcher_of(
                        str(EqualsStringAssertionArgumentsConstructor(
                            surrounded_by_hard_quotes_str('expected contents')))),
                ]
            ).as_remaining_source,
            model_constructor=
            integration_check.constant_relative_file_name(checked_file.name),
            arrangement=
            arrangement_w_tcds(
                non_hds_contents=single_file_in_current_dir(checked_file)
            ),
            expectation=
            Expectation(
                execution=ExecutionExpectation(
                    main_result=matcher_assertions.is_arbitrary_matching_failure()
                ),
            ),
        )
