"""
Test of test-infrastructure: instruction_check.
"""
import pathlib
import unittest
from typing import Sequence, Optional, List

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.file_matcher import FileMatcherSdv
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.ddv_validation import constant_success_validator, \
    DdvValidator
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.file_matcher.file_matcher_ddvs import FileMatcherValueFromPrimitiveDdv
from exactly_lib.test_case_utils.file_matcher.sdvs import FileMatcherSdvFromParts
from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib.test_case_utils.matcher.impls.impl_base_class import MatcherImplBase
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherDdv, FileMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources.parser_classes import ConstantParser
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils, symbol_reference_assertions as sym_asrt
from exactly_lib_test.symbol.data.test_resources import symbol_structure_assertions as asrt_sym
from exactly_lib_test.symbol.test_resources.file_matcher import FileMatcherSdvConstantTestImpl
from exactly_lib_test.test_case.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.test_case_file_structure.test_resources import non_hds_populator, sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    act_dir_contains_exactly, tmp_user_dir_contains_exactly
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check as sut
from exactly_lib_test.test_case_utils.file_matcher.test_resources.model_construction import ModelConstructor, \
    constant_relative_file_name
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_case_utils.test_resources import matcher_assertions
from exactly_lib_test.test_case_utils.test_resources import validation as asrt_validation
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation, is_pass, is_hard_error
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
               parser: Parser[FileMatcherSdv],
               source: ParseSource,
               model: ModelConstructor,
               arrangement: sut.ArrangementPostAct,
               expectation: matcher_assertions.Expectation):
        sut.check(self.tc, parser, source, model, arrangement, expectation)


class TestPopulate(TestCaseBase):
    def test_populate_non_hds(self):
        populated_dir_contents = DirContents([empty_file('non-hds-file.txt')])
        self._check(
            PARSER_THAT_GIVES_MATCHER_THAT_MATCHES,
            utils.single_line_source(),
            constant_relative_file_name('file.txt'),
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
            constant_relative_file_name('file.txt'),
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
                constant_relative_file_name('file.txt'),
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
                constant_relative_file_name('file.txt'),
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

        sdv_that_checks_symbols = FileMatcherSdvThatAssertsThatSymbolsAreAsExpected(self, expectation)

        self._check(
            ConstantParser(sdv_that_checks_symbols),
            utils.single_line_source(),
            constant_relative_file_name('file.txt'),
            sut.ArrangementPostAct(
                symbols=symbol_table_of_arrangement),
            matcher_assertions.Expectation(),
        )


class TestHardError(TestCaseBase):
    def test_expected_hard_error_is_detected(self):
        parser_that_gives_value_that_causes_hard_error = parser_for_constant(
            matchers.MatcherThatReportsHardError()
        )
        self._check(
            parser_that_gives_value_that_causes_hard_error,
            utils.single_line_source(),
            constant_relative_file_name('file.txt'),
            sut.ArrangementPostAct(),
            sut.Expectation(
                is_hard_error=is_hard_error(),
            ))

    def test_missing_hard_error_is_detected(self):
        with self.assertRaises(utils.TestError):
            self._check(
                PARSER_THAT_GIVES_MATCHER_THAT_MATCHES,
                utils.single_line_source(),
                constant_relative_file_name('file.txt'),
                sut.ArrangementPostAct(),
                sut.Expectation(
                    is_hard_error=is_hard_error(),
                ))


class TestMisc(TestCaseBase):
    def test_successful_flow(self):
        self._check(
            PARSER_THAT_GIVES_MATCHER_THAT_MATCHES,
            utils.single_line_source(),
            constant_relative_file_name('file.txt'),
            sut.ArrangementPostAct(),
            is_pass())


class TestFailingExpectations(TestCaseBase):
    def test_fail_due_to_unexpected_result_from_pre_validation(self):
        with self.assertRaises(utils.TestError):
            self._check(ConstantParser(_MATCHER_THAT_MATCHES),
                        utils.single_line_source(),
                        constant_relative_file_name('file.txt'),
                        sut.ArrangementPostAct(),
                        Expectation(
                            validation_pre_sds=asrt_validation.is_arbitrary_validation_failure()),
                        )

    def test_fail_due_to_unexpected_result_from_post_validation(self):
        with self.assertRaises(utils.TestError):
            self._check(ConstantParser(_MATCHER_THAT_MATCHES),
                        utils.single_line_source(),
                        constant_relative_file_name('file.txt'),
                        sut.ArrangementPostAct(),
                        Expectation(
                            validation_post_sds=asrt_validation.is_arbitrary_validation_failure()),
                        )

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(utils.TestError):
            self._check(
                ConstantParser(_MATCHER_THAT_MATCHES),
                utils.single_line_source(),
                constant_relative_file_name('file.txt'),
                sut.ArrangementPostAct(),
                Expectation(
                    main_result=matcher_assertions.is_arbitrary_matching_failure()),
            )

    def test_fail_due_to_fail_of_side_effects_on_files(self):
        with self.assertRaises(utils.TestError):
            self._check(
                ConstantParser(_MATCHER_THAT_MATCHES),
                utils.single_line_source(),
                constant_relative_file_name('file.txt'),
                sut.ArrangementPostAct(),
                Expectation(
                    main_side_effects_on_sds=act_dir_contains_exactly(
                        DirContents([empty_file('non-existing-file.txt')]))),
            )

    def test_that_cwd_for_main_and_post_validation_is_test_root(self):
        self._check(
            ConstantParser(file_matcher_that_raises_test_error_if_cwd_is_is_not_test_root()),
            utils.single_line_source(),
            constant_relative_file_name('file.txt'),
            sut.ArrangementPostAct(),
            is_pass())

    def test_fail_due_to_side_effects_check(self):
        with self.assertRaises(utils.TestError):
            self._check(
                ConstantParser(_MATCHER_THAT_MATCHES),
                utils.single_line_source(),
                constant_relative_file_name('file.txt'),
                sut.ArrangementPostAct(),
                Expectation(
                    main_side_effects_on_tcds=sds_2_tcds_assertion(
                        act_dir_contains_exactly(
                            DirContents([empty_file('non-existing-file.txt')])))),
            )


def file_matcher_that_raises_test_error_if_cwd_is_is_not_test_root() -> FileMatcherSdv:
    def get_matcher(environment: PathResolvingEnvironmentPreOrPostSds) -> FileMatcher:
        return FileMatcherThatRaisesTestErrorIfCwdIsIsNotTestRoot(environment.tcds)

    return FileMatcherSdvFromParts(
        (),
        ValidatorThatRaisesTestErrorIfCwdIsIsNotTestRootAtPostSdsValidation(),
        get_matcher,
    )


class FileMatcherTestImplBase(MatcherImplBase[FileMatcherModel]):
    def __init__(self, result: bool = True):
        super().__init__()
        self._result = result

    @property
    def name(self) -> str:
        return str(type(self))

    def matches(self, model: FileMatcherModel) -> bool:
        self._matches_side_effects(model.path.primitive)
        return self._result

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        self._matches_side_effects(model.path.primitive)
        return self._new_tb().build_result(self._result)

    def _matches_side_effects(self, model: pathlib.Path):
        pass

    @property
    def option_description(self) -> str:
        return str(self)


def parser_for_constant(resolved_value: FileMatcher = constant.MatcherWithConstantResult(True),
                        references: Sequence[SymbolReference] = (),
                        validator: DdvValidator = constant_success_validator()
                        ) -> Parser[FileMatcherSdv]:
    return ConstantParser(
        FileMatcherSdvFromParts(
            references=references,
            validator=validator,
            matcher=lambda tcds: resolved_value,
        ))


class FileMatcherSdvThatAssertsThatSymbolsAreAsExpected(FileMatcherSdv):
    def __init__(self,
                 put: unittest.TestCase,
                 expectation: ValueAssertion[SymbolTable]):
        self._put = put
        self._expectation = expectation

    @property
    def references(self) -> List[SymbolReference]:
        return []

    def resolve(self, symbols: SymbolTable) -> FileMatcherDdv:
        self._expectation.apply_with_message(self._put, symbols, 'symbols given to resolve')

        return FileMatcherValueFromPrimitiveDdv(constant.MatcherWithConstantResult(True))


class ValidatorThatRaisesTestErrorIfCwdIsIsNotTestRootAtPostSdsValidation(DdvValidator):
    def validate_pre_sds_if_applicable(self, hds: HomeDirectoryStructure) -> Optional[TextRenderer]:
        return None

    def validate_post_sds_if_applicable(self, tcds: Tcds) -> Optional[TextRenderer]:
        utils.raise_test_error_if_cwd_is_not_test_root(tcds.sds)
        return None


class FileMatcherThatRaisesTestErrorIfCwdIsIsNotTestRoot(FileMatcherTestImplBase):
    def __init__(self, tcds: Tcds):
        super().__init__()
        self.tcds = tcds

    def _matches_side_effects(self, model: pathlib.Path):
        utils.raise_test_error_if_cwd_is_not_test_root(self.tcds.sds)


PARSER_THAT_GIVES_MATCHER_THAT_MATCHES = parser_for_constant()

_MATCHER_THAT_MATCHES = FileMatcherSdvConstantTestImpl(constant.MatcherWithConstantResult(True))

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
