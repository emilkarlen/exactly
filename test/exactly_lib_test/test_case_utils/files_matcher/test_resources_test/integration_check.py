"""
Test of test-infrastructure: instruction_check.
"""
import unittest
from typing import Sequence, Optional, List

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import ddv_validation
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.files_matcher.impl import files_matchers
from exactly_lib.test_case_utils.files_matcher.new_model_impl import FilesMatcherModelForDir
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, FilesMatcher, FilesMatcherConstructor, \
    FilesMatcherDdv
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources.text_doc_assertions import new_single_string_text_for_test
from exactly_lib_test.section_document.test_resources.parser_classes import ConstantParser
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils, symbol_reference_assertions as sym_asrt
from exactly_lib_test.symbol.data.test_resources import symbol_structure_assertions as asrt_sym
from exactly_lib_test.symbol.test_resources import files_matcher
from exactly_lib_test.symbol.test_resources.files_matcher import FilesMatcherSdvConstantTestImpl, \
    FilesMatcherSdvConstantDdvTestImpl
from exactly_lib_test.test_case.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.test_case_file_structure.test_resources import non_hds_populator, sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    act_dir_contains_exactly, tmp_user_dir_contains_exactly
from exactly_lib_test.test_case_utils.files_matcher.test_resources import integration_check as sut
from exactly_lib_test.test_case_utils.files_matcher.test_resources.model import Model, arbitrary_model
from exactly_lib_test.test_case_utils.test_resources import matcher_assertions
from exactly_lib_test.test_case_utils.test_resources import validation as asrt_validation
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation, is_pass, is_hard_error
from exactly_lib_test.test_case_utils.test_resources.relativity_options import conf_rel_sds, \
    RelativityOptionConfigurationForRelSds
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_file
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    sds_2_tcds_assertion
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
               parser: Parser[FilesMatcherSdv],
               source: ParseSource,
               model: Model,
               arrangement: sut.ArrangementPostAct,
               expectation: matcher_assertions.Expectation):
        sut.check(self.tc, parser, source, model, arrangement, expectation)


class TestPopulate(TestCaseBase):
    def test_populate_non_hds(self):
        populated_dir_contents = DirContents([empty_file('non-home-file.txt')])
        self._check(
            PARSER_THAT_GIVES_MATCHER_THAT_MATCHES,
            utils.single_line_source(),
            arbitrary_model(),
            sut.ArrangementPostAct(
                non_hds_contents=non_hds_populator.rel_option(
                    non_hds_populator.RelNonHdsOptionType.REL_TMP,
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

        sdv_that_checks_symbols = _FilesMatcherSdvThatAssertsThatSymbolsAreAsExpected(self, expectation)

        self._check(
            ConstantParser(sdv_that_checks_symbols),
            utils.single_line_source(),
            arbitrary_model(),
            sut.ArrangementPostAct(
                symbols=symbol_table_of_arrangement),
            matcher_assertions.Expectation(),
        )


class TestHardError(TestCaseBase):
    def test_expected_hard_error_is_detected(self):
        parser_that_gives_value_that_causes_hard_error = parser_for_constant_sdv(
            FilesMatcherSdvConstantDdvTestImpl(
                files_matcher.constant_ddv(
                    _FilesMatcherThatReportsHardError()
                )
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

        model = Model(relativity.path_sdv_for(''))

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
                            validation_pre_sds=asrt_validation.is_arbitrary_validation_failure()),
                        )

    def test_fail_due_to_unexpected_result_from_post_validation(self):
        with self.assertRaises(utils.TestError):
            self._check(ConstantParser(_MATCHER_THAT_MATCHES),
                        utils.single_line_source(),
                        arbitrary_model(),
                        sut.ArrangementPostAct(),
                        Expectation(
                            validation_post_sds=asrt_validation.is_arbitrary_validation_failure()),
                        )

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(utils.TestError):
            self._check(
                ConstantParser(_MATCHER_THAT_MATCHES),
                utils.single_line_source(),
                arbitrary_model(),
                sut.ArrangementPostAct(),
                Expectation(
                    main_result=matcher_assertions.is_arbitrary_matching_failure()),
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
                    main_side_effects_on_tcds=sds_2_tcds_assertion(
                        act_dir_contains_exactly(
                            DirContents([empty_file('non-existing-file.txt')])))),
            )


def _files_matcher_that_raises_test_error_if_cwd_is_is_not_test_root() -> FilesMatcherSdv:
    return FilesMatcherSdvConstantTestImpl(
        True,
        validator=_ValidatorThatRaisesTestErrorIfCwdIsIsNotTestRootAtPostSdsSdvValidation()
    )


def _files_matcher_that_asserts_models_is_expected(put: unittest.TestCase,
                                                   relativity: RelativityOptionConfigurationForRelSds,
                                                   ) -> FilesMatcherSdv:
    return FilesMatcherSdvConstantDdvTestImpl(
        _FilesMatcherDdvThatAssertsModelsIsExpected(put,
                                                    relativity),
    )


class _FilesMatcherThatAssertsModelsIsExpected(FilesMatcher):
    def __init__(self,
                 put: unittest.TestCase,
                 relativity: RelativityOptionConfigurationForRelSds,
                 tcds: Tcds,
                 ):
        self.put = put
        self.relativity = relativity
        self._tcds = tcds

    @property
    def name(self) -> str:
        return str(type(self))

    @property
    def negation(self) -> FilesMatcher:
        raise NotImplementedError('unsupported')

    def matches_emr(self, files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        self.put.assertIsInstance(files_source, FilesMatcherModelForDir, 'files_source')
        assert isinstance(files_source, FilesMatcherModelForDir)
        actual = list(map(lambda fm: fm.path.primitive, files_source.files()))
        actual.sort()

        expected_model_dir = self.relativity.population_dir(self._tcds)

        expected = list(expected_model_dir.iterdir())
        expected.sort()

        self.put.assertEqual(actual,
                             expected)

        return None

    def matches_w_trace(self, model: FilesMatcherModel) -> MatchingResult:
        self.put.assertIsInstance(model, FilesMatcherModelForDir, 'model')
        assert isinstance(model, FilesMatcherModelForDir)
        actual = list(map(lambda fm: fm.path.primitive, model.files()))
        actual.sort()

        expected_model_dir = self.relativity.population_dir(self._tcds)

        expected = list(expected_model_dir.iterdir())
        expected.sort()

        self.put.assertEqual(actual,
                             expected)

        return self._new_tb().build_result(True)


class _FilesMatcherDdvThatAssertsModelsIsExpected(FilesMatcherDdv):
    def __init__(self,
                 put: unittest.TestCase,
                 relativity: RelativityOptionConfigurationForRelSds,
                 ):
        self.put = put
        self.relativity = relativity

    def value_of_any_dependency(self, tcds: Tcds) -> FilesMatcherConstructor:
        return files_matchers.ConstantConstructor(
            _FilesMatcherThatAssertsModelsIsExpected(
                self.put,
                self.relativity,
                tcds,
            )
        )


class _FilesMatcherThatReportsHardError(FilesMatcher):

    @property
    def name(self) -> str:
        return str(type(self))

    @property
    def negation(self) -> FilesMatcher:
        raise NotImplementedError('unsupported')

    def matches_emr(self, files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        raise HardErrorException(
            new_single_string_text_for_test('unconditional hard error')
        )

    def matches_w_trace(self, model: FilesMatcherModel) -> MatchingResult:
        raise HardErrorException(
            new_single_string_text_for_test('unconditional hard error')
        )


class _ValidatorThatRaisesTestErrorIfCwdIsIsNotTestRootAtPostSdsSdvValidation(DdvValidator):
    def validate_pre_sds_if_applicable(self, hds: HomeDirectoryStructure) -> Optional[TextRenderer]:
        return None

    def validate_post_sds_if_applicable(self, tcds: Tcds) -> Optional[TextRenderer]:
        utils.raise_test_error_if_cwd_is_not_test_root(tcds.sds)
        return None


def parser_for_constant(resolved_value: bool,
                        references: Sequence[SymbolReference] = (),
                        validator: DdvValidator = ddv_validation.constant_success_validator()
                        ) -> Parser[FilesMatcherSdv]:
    return ConstantParser(
        FilesMatcherSdvConstantTestImpl(
            resolved_value=resolved_value,
            references=references,
            validator=validator,
        ))


def parser_for_constant_sdv(result: FilesMatcherSdv) -> Parser[FilesMatcherSdv]:
    return ConstantParser(result)


class _FilesMatcherSdvThatAssertsThatSymbolsAreAsExpected(FilesMatcherSdv):
    def __init__(self,
                 put: unittest.TestCase,
                 expectation: ValueAssertion[SymbolTable]):
        self._put = put
        self._expectation = expectation

    @property
    def references(self) -> List[SymbolReference]:
        return []

    def resolve(self, symbols: SymbolTable) -> FilesMatcherDdv:
        self._expectation.apply_with_message(self._put, symbols, 'symbols given to resolve')

        return files_matcher.value_with_result(True)


PARSER_THAT_GIVES_MATCHER_THAT_MATCHES = parser_for_constant(True)

_MATCHER_THAT_MATCHES = FilesMatcherSdvConstantTestImpl(True)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
