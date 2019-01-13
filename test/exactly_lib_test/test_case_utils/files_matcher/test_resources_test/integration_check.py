"""
Test of test-infrastructure: instruction_check.
"""
import unittest

from typing import Sequence, Optional, List

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.files_matcher import FilesMatcherResolver, FilesMatcherValue, Environment, FilesMatcherModel
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds, PathResolvingEnvironment
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case import pre_or_post_validation
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib.test_case_utils.files_matcher.new_model_impl import FilesMatcherModelForDir
from exactly_lib.type_system.error_message import ErrorMessageResolver, ConstantErrorMessageResolver
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources.parser_classes import ConstantParser
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils, symbol_reference_assertions as sym_asrt
from exactly_lib_test.symbol.data.test_resources import symbol_structure_assertions as asrt_sym
from exactly_lib_test.symbol.test_resources.files_matcher import FilesMatcherResolverConstantTestImpl, \
    FilesMatcherResolverConstantValueTestImpl, FilesMatcherValueTestImpl
from exactly_lib_test.test_case.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.test_case_file_structure.test_resources import non_home_populator, sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    act_dir_contains_exactly, tmp_user_dir_contains_exactly
from exactly_lib_test.test_case_utils.files_matcher.test_resources import integration_check as sut
from exactly_lib_test.test_case_utils.files_matcher.test_resources.model import Model, arbitrary_model
from exactly_lib_test.test_case_utils.test_resources import matcher_assertions
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation, is_pass, is_hard_error
from exactly_lib_test.test_case_utils.test_resources.relativity_options import conf_rel_sds, \
    RelativityOptionConfigurationForRelSds
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_file
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    sds_2_home_and_sds_assertion
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


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
               parser: Parser[FilesMatcherResolver],
               source: ParseSource,
               model: Model,
               arrangement: sut.ArrangementPostAct,
               expectation: matcher_assertions.Expectation):
        sut.check(self.tc, parser, source, model, arrangement, expectation)


class TestPopulate(TestCaseBase):
    def test_populate_non_home(self):
        populated_dir_contents = DirContents([empty_file('non-home-file.txt')])
        self._check(
            PARSER_THAT_GIVES_MATCHER_THAT_MATCHES,
            utils.single_line_source(),
            arbitrary_model(),
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
            arbitrary_model(),
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
                    True,
                    references=unexpected_symbol_usages
                ),
                utils.single_line_source(),
                arbitrary_model(),
                sut.ArrangementPostAct(),
                matcher_assertions.Expectation(),
            )

    def test_that_fails_due_to_missing_symbol_reference(self):
        with self.assertRaises(utils.TestError):
            symbol_usages_of_matcher = []
            symbol_usages_of_expectation = [data_symbol_utils.symbol_reference('symbol_name')]
            self._check(
                parser_for_constant(
                    True,
                    references=symbol_usages_of_matcher
                ),
                utils.single_line_source(),
                arbitrary_model(),
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

        resolver_that_checks_symbols = _FilesMatcherResolverThatAssertsThatSymbolsAreAsExpected(self, expectation)

        self._check(
            ConstantParser(resolver_that_checks_symbols),
            utils.single_line_source(),
            arbitrary_model(),
            sut.ArrangementPostAct(
                symbols=symbol_table_of_arrangement),
            matcher_assertions.Expectation(),
        )


class TestHardError(TestCaseBase):
    def test_expected_hard_error_is_detected(self):
        parser_that_gives_value_that_causes_hard_error = parser_for_constant_resolver(
            FilesMatcherResolverConstantValueTestImpl(
                _FilesMatcherValueThatReportsHardError()
            )
        )
        self._check(
            parser_that_gives_value_that_causes_hard_error,
            utils.single_line_source(),
            arbitrary_model(),
            sut.ArrangementPostAct(),
            sut.Expectation(
                is_hard_error=is_hard_error(),
            ))

    def test_missing_hard_error_is_detected(self):
        with self.assertRaises(utils.TestError):
            self._check(
                PARSER_THAT_GIVES_MATCHER_THAT_MATCHES,
                utils.single_line_source(),
                arbitrary_model(),
                sut.ArrangementPostAct(),
                sut.Expectation(
                    is_hard_error=is_hard_error(),
                ))


class TestMisc(TestCaseBase):
    def test_successful_flow(self):
        self._check(
            PARSER_THAT_GIVES_MATCHER_THAT_MATCHES,
            utils.single_line_source(),
            arbitrary_model(),
            sut.ArrangementPostAct(),
            is_pass())

    def test_model_is_correct(self):
        relativity = conf_rel_sds(RelSdsOptionType.REL_TMP)

        model = Model(relativity.file_ref_resolver_for(''))

        expected_files_from_model = DirContents([
            empty_file('file-1'),
            empty_file('file-2'),
        ])

        self._check(
            ConstantParser(_files_matcher_that_asserts_models_is_expected(self,
                                                                          relativity)),
            utils.single_line_source(),
            model,
            sut.ArrangementPostAct(
                sds_contents=relativity.populator_for_relativity_option_root__sds(expected_files_from_model)
            ),
            is_pass())


class TestFailingExpectations(TestCaseBase):
    def test_fail_due_to_unexpected_result_from_pre_validation(self):
        with self.assertRaises(utils.TestError):
            self._check(ConstantParser(_MATCHER_THAT_MATCHES),
                        utils.single_line_source(),
                        arbitrary_model(),
                        sut.ArrangementPostAct(),
                        Expectation(
                            validation_pre_sds=matcher_assertions.arbitrary_validation_failure()),
                        )

    def test_fail_due_to_unexpected_result_from_post_validation(self):
        with self.assertRaises(utils.TestError):
            self._check(ConstantParser(_MATCHER_THAT_MATCHES),
                        utils.single_line_source(),
                        arbitrary_model(),
                        sut.ArrangementPostAct(),
                        Expectation(
                            validation_post_sds=matcher_assertions.arbitrary_validation_failure()),
                        )

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(utils.TestError):
            self._check(
                ConstantParser(_MATCHER_THAT_MATCHES),
                utils.single_line_source(),
                arbitrary_model(),
                sut.ArrangementPostAct(),
                Expectation(
                    main_result=matcher_assertions.arbitrary_matching_failure()),
            )

    def test_fail_due_to_fail_of_side_effects_on_files(self):
        with self.assertRaises(utils.TestError):
            self._check(
                ConstantParser(_MATCHER_THAT_MATCHES),
                utils.single_line_source(),
                arbitrary_model(),
                sut.ArrangementPostAct(),
                Expectation(
                    main_side_effects_on_sds=act_dir_contains_exactly(
                        DirContents([empty_file('non-existing-file.txt')]))),
            )

    def test_that_cwd_for_main_and_post_validation_is_test_root(self):
        self._check(
            ConstantParser(_files_matcher_that_raises_test_error_if_cwd_is_is_not_test_root()),
            utils.single_line_source(),
            arbitrary_model(),
            sut.ArrangementPostAct(),
            is_pass())

    def test_fail_due_to_side_effects_check(self):
        with self.assertRaises(utils.TestError):
            self._check(
                ConstantParser(_MATCHER_THAT_MATCHES),
                utils.single_line_source(),
                arbitrary_model(),
                sut.ArrangementPostAct(),
                Expectation(
                    main_side_effects_on_home_and_sds=sds_2_home_and_sds_assertion(
                        act_dir_contains_exactly(
                            DirContents([empty_file('non-existing-file.txt')])))),
            )


def _files_matcher_that_raises_test_error_if_cwd_is_is_not_test_root() -> FilesMatcherResolver:
    return FilesMatcherResolverConstantTestImpl(
        True,
        validator=_ValidatorThatRaisesTestErrorIfCwdIsIsNotTestRootAtPostSdsValidation()
    )


def _files_matcher_that_asserts_models_is_expected(put: unittest.TestCase,
                                                   relativity: RelativityOptionConfigurationForRelSds,
                                                   ) -> FilesMatcherResolver:
    return FilesMatcherResolverConstantValueTestImpl(
        _FilesMatcherValueThatAssertsModelsIsExpected(put,
                                                      relativity),
    )


class _FilesMatcherValueThatAssertsModelsIsExpected(FilesMatcherValue):
    def __init__(self,
                 put: unittest.TestCase,
                 relativity: RelativityOptionConfigurationForRelSds,
                 ):
        self.put = put
        self.relativity = relativity

    @property
    def negation(self):
        raise NotImplementedError('should not be used')

    def matches(self,
                environment: Environment,
                files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        self.put.assertIsInstance(environment, Environment, 'environment')
        self.put.assertIsInstance(files_source, FilesMatcherModelForDir, 'files_source')
        assert isinstance(files_source, FilesMatcherModelForDir)
        actual = list(map(lambda fm: fm.path, files_source.files()))
        actual.sort()

        expected_model_dir = self.relativity.population_dir(environment.path_resolving_environment.home_and_sds)

        expected = list(expected_model_dir.iterdir())
        expected.sort()

        self.put.assertEqual(actual,
                             expected)

        return None


class _FilesMatcherValueThatReportsHardError(FilesMatcherValue):
    @property
    def negation(self):
        raise NotImplementedError('should not be used')

    def matches(self,
                environment: Environment,
                files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        raise HardErrorException(ConstantErrorMessageResolver('unconditional hard error'))


class _ValidatorThatRaisesTestErrorIfCwdIsIsNotTestRootAtPostSdsValidation(PreOrPostSdsValidator):
    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[str]:
        return None

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[str]:
        utils.raise_test_error_if_cwd_is_not_test_root(environment.sds)
        return None


def parser_for_constant(resolved_value: bool,
                        references: Sequence[SymbolReference] = (),
                        validator: PreOrPostSdsValidator = pre_or_post_validation.ConstantSuccessValidator()
                        ) -> Parser[FilesMatcherResolver]:
    return ConstantParser(
        FilesMatcherResolverConstantTestImpl(
            resolved_value=resolved_value,
            references=references,
            validator=validator,
        ))


def parser_for_constant_resolver(result: FilesMatcherResolver) -> Parser[FilesMatcherResolver]:
    return ConstantParser(result)


class _FilesMatcherResolverThatAssertsThatSymbolsAreAsExpected(FilesMatcherResolver):
    def __init__(self,
                 put: unittest.TestCase,
                 expectation: ValueAssertion[SymbolTable]):
        self._put = put
        self._expectation = expectation

    @property
    def references(self) -> List[SymbolReference]:
        return []

    def resolve(self, symbols: SymbolTable) -> FilesMatcherValue:
        self._expectation.apply_with_message(self._put, symbols, 'symbols given to resolve')

        return FilesMatcherValueTestImpl(True)

    def validator(self) -> PreOrPostSdsValidator:
        return ValidatorThatAssertsThatSymbolsInEnvironmentAreAsExpected(self._put,
                                                                         self._expectation)


class ValidatorThatAssertsThatSymbolsInEnvironmentAreAsExpected(PreOrPostSdsValidator):
    def __init__(self,
                 put: unittest.TestCase,
                 expectation: ValueAssertion[SymbolTable]):
        self._put = put
        self._expectation = expectation

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[str]:
        return self._apply(environment)

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[str]:
        return self._apply(environment)

    def _apply(self, environment: PathResolvingEnvironment) -> Optional[str]:
        self._expectation.apply_with_message(self._put, environment.symbols,
                                             'symbols given to validator')

        return None


class ValidatorThatRaisesTestErrorIfCwdIsIsNotTestRootAtPostSdsValidation(PreOrPostSdsValidator):
    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[str]:
        return None

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[str]:
        utils.raise_test_error_if_cwd_is_not_test_root(environment.sds)
        return None


PARSER_THAT_GIVES_MATCHER_THAT_MATCHES = parser_for_constant(True)

_MATCHER_THAT_MATCHES = FilesMatcherResolverConstantTestImpl(True)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())