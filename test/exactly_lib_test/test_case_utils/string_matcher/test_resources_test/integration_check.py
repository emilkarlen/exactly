"""
Test of test-infrastructure: instruction_check.
"""
import unittest
from typing import Sequence, Optional, List, Set

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds, PathResolvingEnvironment, PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import pre_or_post_validation
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.string_matcher.resolvers import StringMatcherResolverFromParts
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.type_system.logic.string_matcher import StringMatcher, StringMatcherValue, FileToCheck
from exactly_lib.type_system.logic.string_matcher_values import StringMatcherConstantValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources.text_doc_assertions import new_single_string_text_for_test
from exactly_lib_test.section_document.test_resources.parser_classes import ConstantParser
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils, symbol_reference_assertions as sym_asrt
from exactly_lib_test.symbol.data.test_resources import symbol_structure_assertions as asrt_sym
from exactly_lib_test.symbol.test_resources.string_matcher import StringMatcherResolverConstantTestImpl
from exactly_lib_test.test_case.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.test_case_file_structure.test_resources import non_home_populator, sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    act_dir_contains_exactly, tmp_user_dir_contains_exactly
from exactly_lib_test.test_case_utils.string_matcher.test_resources import integration_check as sut
from exactly_lib_test.test_case_utils.string_matcher.test_resources.model_construction import ModelBuilder, empty_model
from exactly_lib_test.test_case_utils.string_matcher.test_resources.string_matchers import StringMatcherTestImplBase
from exactly_lib_test.test_case_utils.test_resources import matcher_assertions
from exactly_lib_test.test_case_utils.test_resources import validation as asrt_validation
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation, is_pass, is_hard_error
from exactly_lib_test.test_resources.files.file_checks import FileChecker
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_file
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    sds_2_home_and_sds_assertion
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.test_resources.string_matchers import StringMatcherConstant


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestFailingExpectations))
    ret_val.addTest(unittest.makeSuite(TestPopulate))
    ret_val.addTest(unittest.makeSuite(TestSymbolReferences))
    ret_val.addTest(unittest.makeSuite(TestHardError))
    ret_val.addTest(unittest.makeSuite(TestMisc))
    return ret_val


class TestCaseBase(unittest.TestCase):
    def setUp(self):
        self.tc = utils.TestCaseWithTestErrorAsFailureException()

    def _check(self,
               parser: Parser[StringMatcherResolver],
               source: ParseSource,
               model: ModelBuilder,
               arrangement: sut.ArrangementPostAct,
               expectation: matcher_assertions.Expectation):
        sut.check(self.tc, parser, source, model, arrangement, expectation)


class TestPopulate(TestCaseBase):
    def test_populate_non_home(self):
        populated_dir_contents = DirContents([empty_file('non-home-file.txt')])
        self._check(
            PARSER_THAT_GIVES_MATCHER_THAT_MATCHES,
            utils.single_line_source(),
            empty_model(),
            sut.ArrangementPostAct(
                non_home_contents=non_home_populator.rel_option(
                    non_home_populator.RelNonHomeOptionType.REL_TMP,
                    populated_dir_contents)),
            matcher_assertions.Expectation(
                main_side_effects_on_sds=tmp_user_dir_contains_exactly(
                    populated_dir_contents)),
        )

    def test_populate_sds(self):
        populated_dir_contents = DirContents([empty_file('sds-file.txt')])
        self._check(
            PARSER_THAT_GIVES_MATCHER_THAT_MATCHES,
            utils.single_line_source(),
            empty_model(),
            sut.ArrangementPostAct(
                sds_contents=sds_populator.contents_in(
                    sds_populator.RelSdsOptionType.REL_TMP,
                    populated_dir_contents)),
            matcher_assertions.Expectation(
                main_side_effects_on_sds=tmp_user_dir_contains_exactly(
                    populated_dir_contents)),
        )


class TestSymbolReferences(TestCaseBase):
    def test_that_default_expectation_assumes_no_symbol_usages(self):
        with self.assertRaises(utils.TestError):
            unexpected_symbol_usages = [data_symbol_utils.symbol_reference('symbol_name')]
            self._check(
                parser_for_constant(
                    references=unexpected_symbol_usages
                ),
                utils.single_line_source(),
                empty_model(),
                sut.ArrangementPostAct(),
                matcher_assertions.Expectation(),
            )

    def test_that_fails_due_to_missing_symbol_reference(self):
        with self.assertRaises(utils.TestError):
            symbol_usages_of_matcher = []
            symbol_usages_of_expectation = [data_symbol_utils.symbol_reference('symbol_name')]
            self._check(
                parser_for_constant(
                    references=symbol_usages_of_matcher
                ),
                utils.single_line_source(),
                empty_model(),
                sut.ArrangementPostAct(),
                matcher_assertions.Expectation(
                    symbol_usages=sym_asrt.equals_symbol_references(symbol_usages_of_expectation)),
            )

    def test_that_symbols_from_arrangement_exist_in_environment(self):
        symbol_name = 'symbol_name'
        symbol_value = 'the symbol value'
        symbol_table_of_arrangement = data_symbol_utils.symbol_table_with_single_string_value(symbol_name,
                                                                                              symbol_value)
        expected_symbol_table = data_symbol_utils.symbol_table_with_single_string_value(symbol_name,
                                                                                        symbol_value)
        expectation = asrt_sym.equals_symbol_table(expected_symbol_table)

        resolver_that_checks_symbols = StringMatcherResolverThatAssertsThatSymbolsAreAsExpected(self, expectation)

        self._check(
            ConstantParser(resolver_that_checks_symbols),
            utils.single_line_source(),
            empty_model(),
            sut.ArrangementPostAct(
                symbols=symbol_table_of_arrangement),
            matcher_assertions.Expectation(),
        )


class TestHardError(TestCaseBase):
    def test_expected_hard_error_is_detected(self):
        parser_that_gives_value_that_causes_hard_error = parser_for_constant(
            _StringMatcherThatReportsHardError()
        )
        self._check(
            parser_that_gives_value_that_causes_hard_error,
            utils.single_line_source(),
            empty_model(),
            sut.ArrangementPostAct(),
            sut.Expectation(
                is_hard_error=is_hard_error(),
            ))

    def test_missing_hard_error_is_detected(self):
        with self.assertRaises(utils.TestError):
            self._check(
                PARSER_THAT_GIVES_MATCHER_THAT_MATCHES,
                utils.single_line_source(),
                empty_model(),
                sut.ArrangementPostAct(),
                sut.Expectation(
                    is_hard_error=is_hard_error(),
                ))


class TestMisc(TestCaseBase):
    def test_successful_flow(self):
        self._check(
            PARSER_THAT_GIVES_MATCHER_THAT_MATCHES,
            utils.single_line_source(),
            empty_model(),
            sut.ArrangementPostAct(),
            is_pass())

    def test_model_is_correct(self):
        contents = 'expected model file\ncontents'

        mode = empty_model().with_original_file_contents(contents)

        self._check(
            ConstantParser(string_matcher_that_asserts_models_is_expected(self,
                                                                          contents)),
            utils.single_line_source(),
            mode,
            sut.ArrangementPostAct(),
            is_pass())


class TestFailingExpectations(TestCaseBase):
    def test_fail_due_to_unexpected_result_from_pre_validation(self):
        with self.assertRaises(utils.TestError):
            self._check(ConstantParser(_MATCHER_THAT_MATCHES),
                        utils.single_line_source(),
                        empty_model(),
                        sut.ArrangementPostAct(),
                        Expectation(
                            validation_pre_sds=asrt_validation.is_arbitrary_validation_failure()),
                        )

    def test_fail_due_to_unexpected_result_from_post_validation(self):
        with self.assertRaises(utils.TestError):
            self._check(ConstantParser(_MATCHER_THAT_MATCHES),
                        utils.single_line_source(),
                        empty_model(),
                        sut.ArrangementPostAct(),
                        Expectation(
                            validation_post_sds=asrt_validation.is_arbitrary_validation_failure()),
                        )

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(utils.TestError):
            self._check(
                ConstantParser(_MATCHER_THAT_MATCHES),
                utils.single_line_source(),
                empty_model(),
                sut.ArrangementPostAct(),
                Expectation(
                    main_result=matcher_assertions.is_arbitrary_matching_failure()),
            )

    def test_fail_due_to_fail_of_side_effects_on_files(self):
        with self.assertRaises(utils.TestError):
            self._check(
                ConstantParser(_MATCHER_THAT_MATCHES),
                utils.single_line_source(),
                empty_model(),
                sut.ArrangementPostAct(),
                Expectation(
                    main_side_effects_on_sds=act_dir_contains_exactly(
                        DirContents([empty_file('non-existing-file.txt')]))),
            )

    def test_that_cwd_for_main_and_post_validation_is_test_root(self):
        self._check(
            ConstantParser(string_matcher_that_raises_test_error_if_cwd_is_is_not_test_root()),
            utils.single_line_source(),
            empty_model(),
            sut.ArrangementPostAct(),
            is_pass())

    def test_fail_due_to_side_effects_check(self):
        with self.assertRaises(utils.TestError):
            self._check(
                ConstantParser(_MATCHER_THAT_MATCHES),
                utils.single_line_source(),
                empty_model(),
                sut.ArrangementPostAct(),
                Expectation(
                    main_side_effects_on_home_and_sds=sds_2_home_and_sds_assertion(
                        act_dir_contains_exactly(
                            DirContents([empty_file('non-existing-file.txt')])))),
            )


def string_matcher_that_raises_test_error_if_cwd_is_is_not_test_root() -> StringMatcherResolver:
    def get_matcher(environment: PathResolvingEnvironmentPreOrPostSds) -> StringMatcher:
        return StringMatcherThatRaisesTestErrorIfCwdIsIsNotTestRoot(environment.home_and_sds)

    return StringMatcherResolverFromParts(
        (),
        ValidatorThatRaisesTestErrorIfCwdIsIsNotTestRootAtPostSdsValidation(),
        no_resolving_dependencies,
        get_matcher,
    )


def string_matcher_that_asserts_models_is_expected(put: unittest.TestCase,
                                                   expected_model_string_contents: str
                                                   ) -> StringMatcherResolver:
    def get_matcher(environment: PathResolvingEnvironmentPreOrPostSds) -> StringMatcher:
        return StringMatcherThatAssertsModelsIsExpected(put, expected_model_string_contents)

    return StringMatcherResolverFromParts(
        (),
        pre_or_post_validation.ConstantSuccessValidator(),
        no_resolving_dependencies,
        get_matcher,
    )


class _StringMatcherThatReportsHardError(StringMatcher):
    @property
    def name(self) -> str:
        return 'unconditional HARD ERROR'

    @property
    def option_description(self) -> str:
        return 'unconditional HARD ERROR'

    def matches_emr(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        raise HardErrorException(new_single_string_text_for_test('unconditional hard error'))

    def matches_w_trace(self, model: FileToCheck) -> MatchingResult:
        raise HardErrorException(new_single_string_text_for_test('unconditional hard error'))


def parser_for_constant(resolved_value: StringMatcher = StringMatcherConstant(None),
                        references: Sequence[SymbolReference] = (),
                        validator: PreOrPostSdsValidator = pre_or_post_validation.ConstantSuccessValidator()
                        ) -> Parser[StringMatcherResolver]:
    return ConstantParser(
        StringMatcherResolverConstantTestImpl(
            resolved_value=resolved_value,
            references=references,
            validator=validator,
        ))


class StringMatcherResolverThatAssertsThatSymbolsAreAsExpected(StringMatcherResolver):
    def __init__(self,
                 put: unittest.TestCase,
                 expectation: ValueAssertion[SymbolTable]):
        self._put = put
        self._expectation = expectation

    @property
    def references(self) -> List[SymbolReference]:
        return []

    def resolve(self, symbols: SymbolTable) -> StringMatcherValue:
        self._expectation.apply_with_message(self._put, symbols, 'symbols given to resolve')

        return StringMatcherConstantValue(StringMatcherConstant(None))

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return ValidatorThatAssertsThatSymbolsInEnvironmentAreAsExpected(self._put,
                                                                         self._expectation)


class ValidatorThatAssertsThatSymbolsInEnvironmentAreAsExpected(PreOrPostSdsValidator):
    def __init__(self,
                 put: unittest.TestCase,
                 expectation: ValueAssertion[SymbolTable]):
        self._put = put
        self._expectation = expectation

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[TextRenderer]:
        return self._apply(environment)

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
        return self._apply(environment)

    def _apply(self, environment: PathResolvingEnvironment) -> Optional[TextRenderer]:
        self._expectation.apply_with_message(self._put, environment.symbols,
                                             'symbols given to validator')

        return None


class ValidatorThatRaisesTestErrorIfCwdIsIsNotTestRootAtPostSdsValidation(PreOrPostSdsValidator):
    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[TextRenderer]:
        return None

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
        utils.raise_test_error_if_cwd_is_not_test_root(environment.sds)
        return None


class StringMatcherThatRaisesTestErrorIfCwdIsIsNotTestRoot(StringMatcherTestImplBase):
    def __init__(self, tcds: HomeAndSds):
        super().__init__()
        self.tcds = tcds

    @property
    def name(self) -> str:
        return str(type(self))

    def _matches_side_effects(self, model: FileToCheck):
        utils.raise_test_error_if_cwd_is_not_test_root(self.tcds.sds)


class StringMatcherThatAssertsModelsIsExpected(StringMatcherTestImplBase):
    def __init__(self,
                 put: unittest.TestCase,
                 expected_model_string_contents: str):
        super().__init__()
        self.put = put
        self.expected_model_string_contents = expected_model_string_contents

    @property
    def name(self) -> str:
        return str(type(self))

    def _matches_side_effects(self, model: FileToCheck):
        self._assert_original_file_is_existing_regular_file_with_expected_contents(model)
        self._assert_transformer_is_identity_transformer(model)

    def _assert_original_file_is_existing_regular_file_with_expected_contents(self, model: FileToCheck):
        checker = FileChecker(self.put, 'original file')
        checker.assert_is_plain_file_with_contents(model.original_file_path.primitive,
                                                   self.expected_model_string_contents)

    def _assert_transformer_is_identity_transformer(self, model: FileToCheck):
        checker = FileChecker(self.put, 'transformed file')
        checker.assert_is_plain_file_with_contents(model.transformed_file_path(),
                                                   self.expected_model_string_contents)


PARSER_THAT_GIVES_MATCHER_THAT_MATCHES = parser_for_constant()

_MATCHER_THAT_MATCHES = StringMatcherConstant(None)


def no_resolving_dependencies(symbols: SymbolTable) -> Set[DirectoryStructurePartition]:
    return set()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
