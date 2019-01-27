import unittest

from typing import Iterable, List

from exactly_lib.definitions.test_case import file_check_properties
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib.test_case_utils.string_transformer.resolvers import StringTransformerConstant
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_file_structure.test_resources import sds_populator
from exactly_lib_test.test_case_utils.file_matcher.test_resources import model_construction
from exactly_lib_test.test_case_utils.file_matcher.test_resources import parse_test_configuration as tc
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.arguments_building import args as sm_args
from exactly_lib_test.test_case_utils.test_resources import matcher_assertions
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForNoneIsSuccess
from exactly_lib_test.test_resources.files.file_structure import empty_file, File, DirContents, empty_dir, \
    FileSystemElement
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestHardErrorWhenActualFileDoesNotExist(),
        TestHardErrorWhenActualFileIsADirectory(),
        ActualFileIsEmpty(),
        ActualFileIsEmptyAfterTransformation(),
    ])


def arguments_for(additional_arguments: str, following_lines=()) -> Arguments:
    return Arguments(file_check_properties.REGULAR_FILE_CONTENTS + ' ' + additional_arguments,
                     following_lines)


def source_for_lines(argument_lines: List[str]) -> ParseSource:
    return source_for(argument_lines[0], argument_lines[1:])


def source_for(argument_tail: str, following_lines=()) -> ParseSource:
    return arguments_for(argument_tail).followed_by_lines(following_lines).as_remaining_source


def single_file_in_current_dir(f: FileSystemElement) -> sds_populator.SdsPopulator:
    return sds_populator.contents_in(
        RelSdsOptionType.REL_ACT,
        DirContents([f])
    )


class TestHardErrorWhenActualFileDoesNotExist(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        self._check(
            source=
            source_for(
                sm_args('{maybe_not} {empty}',
                        maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
            model=
            model_construction.constant_relative_file_name('non-existing.txt'),
            arrangement=
            ArrangementPostAct(),
            expectation=
            Expectation(
                main_result=matcher_assertions.is_hard_error()
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
            model=
            model_construction.constant_relative_file_name(checked_file.name),
            arrangement=
            ArrangementPostAct(
                sds_contents=single_file_in_current_dir(checked_file)
            ),
            expectation=
            Expectation(
                main_result=matcher_assertions.is_hard_error()
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
            model=
            model_construction.constant_relative_file_name(checked_file.name),
            arrangement=
            ArrangementPostAct(
                sds_contents=single_file_in_current_dir(checked_file)
            ),
            expectation=
            Expectation(
                main_result=maybe_not.pass__if_positive__fail__if_negative
            ),
        )


class ActualFileIsEmptyAfterTransformation(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        # ARRANGE #

        named_transformer = NameAndValue('the_transformer',
                                         StringTransformerConstant(
                                             DeleteEverythingStringTransformer()))

        checked_file = File('actual.txt', 'some\ntext')

        symbols = SymbolTable({
            named_transformer.name: container(named_transformer.value)
        })

        expected_symbol_reference_to_transformer = is_reference_to_string_transformer(named_transformer.name)

        expected_symbol_usages = asrt.matches_sequence([expected_symbol_reference_to_transformer])

        # ACT & ASSERT #

        self._check_with_source_variants(
            arguments=
            arguments_for(
                sm_args('{transform_option} {the_transformer} {maybe_not} {empty}',
                        the_transformer=named_transformer.name,
                        maybe_not=maybe_not.nothing__if_positive__not_option__if_negative)),
            model=
            model_construction.constant_relative_file_name(checked_file.name),
            arrangement=
            ArrangementPostAct(
                sds_contents=single_file_in_current_dir(checked_file),
                symbols=symbols,
            ),
            expectation=
            Expectation(
                main_result=maybe_not.pass__if_positive__fail__if_negative,
                symbol_usages=expected_symbol_usages),
        )


class DeleteEverythingStringTransformer(StringTransformer):
    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(lambda x: '', lines)
