"""
Test of test-infrastructure: instruction_check.
"""
import pathlib
import unittest
from typing import List, Sequence, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.logic_type_sdv import MatcherTypeSdv
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.ddv_validation import ConstantDdvValidator, DdvValidator
from exactly_lib.test_case_file_structure import sandbox_directory_structure as sds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import RelHdsOptionType, RelOptionType
from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.impls import advs
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherWTraceAndNegation, MODEL, \
    MatchingResult, Failure, MatcherAdv
from exactly_lib.type_system.value_type import ValueType, LogicValueType
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources.parser_classes import ConstantParser
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils, symbol_reference_assertions as sym_asrt
from exactly_lib_test.symbol.data.test_resources import symbol_structure_assertions as asrt_sym
from exactly_lib_test.test_case.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.test_case.test_resources.arrangements import ActResultProducerFromActResult
from exactly_lib_test.test_case_file_structure.test_resources import non_hds_populator, hds_contents_check, \
    hds_populators
from exactly_lib_test.test_case_file_structure.test_resources import tcds_contents_assertions as asrt_tcds_contents
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    tmp_user_dir_contains_exactly
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers, integration_check as sut
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import Expectation
from exactly_lib_test.test_case_utils.matcher.test_resources.matchers import MatcherThatReportsHardError
from exactly_lib_test.test_case_utils.test_resources import matcher_assertions
from exactly_lib_test.test_case_utils.test_resources import validation as asrt_validation
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import is_hard_error
from exactly_lib_test.test_resources.files.file_structure import empty_file, DirContents, File
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import sds_2_tcds_assertion
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt, file_assertions
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

EXPECTED_LOGIC_TYPE_FOR_TEST = LogicValueType.LINE_MATCHER
UNEXPECTED_LOGIC_TYPE_FOR_TEST = LogicValueType.FILE_MATCHER

EXPECTED_VALUE_TYPE_FOR_TEST = ValueType.LINE_MATCHER
UNEXPECTED_VALUE_TYPE_FOR_TEST = ValueType.FILE_MATCHER


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestDefault))
    ret_val.addTest(unittest.makeSuite(TestTypes))
    ret_val.addTest(unittest.makeSuite(TestFailingExpectations))
    ret_val.addTest(unittest.makeSuite(TestSymbolReferences))
    ret_val.addTest(unittest.makeSuite(TestHardError))
    ret_val.addTest(unittest.makeSuite(TestPopulateDirectoriesAndCwd))
    return ret_val


class TestCaseBase(unittest.TestCase):
    def setUp(self):
        self.tc = utils.TestCaseWithTestErrorAsFailureException()

    def _check_line_matcher_type(self,
                                 source: ParseSource,
                                 model: int,
                                 parser: Parser[MatcherTypeSdv[int]],
                                 arrangement: sut.Arrangement,
                                 expectation: sut.Expectation):
        sut.check(self.tc, source, sut.constant_model(model), parser, arrangement,
                  EXPECTED_LOGIC_TYPE_FOR_TEST,
                  EXPECTED_VALUE_TYPE_FOR_TEST,
                  expectation)


class TestSymbolReferences(TestCaseBase):
    def test_that_fails_due_to_missing_symbol_reference(self):
        with self.assertRaises(utils.TestError):
            symbol_usages_of_matcher = []
            symbol_usages_of_expectation = [data_symbol_utils.symbol_reference('symbol_name')]
            self._check_line_matcher_type(
                utils.single_line_source(),
                ARBITRARY_MODEL,
                _constant_line_matcher_type_parser_of_matcher_sdv(
                    matchers.sdv_from_primitive_value(references=symbol_usages_of_matcher)
                ),
                sut.Arrangement(),
                sut.Expectation(
                    symbol_references=sym_asrt.equals_symbol_references(symbol_usages_of_expectation)),
            )

    def test_that_symbols_from_arrangement_exist_in_environment(self):
        symbol_name = 'symbol_name'
        symbol_value = 'the symbol value'
        symbol_table_of_arrangement = data_symbol_utils.symbol_table_with_single_string_value(symbol_name,
                                                                                              symbol_value)
        expected_symbol_table = data_symbol_utils.symbol_table_with_single_string_value(symbol_name,
                                                                                        symbol_value)
        expectation = asrt_sym.equals_symbol_table(expected_symbol_table)

        sdv_that_checks_symbols = MatcherSdvThatAssertsThatSymbolsAreAsExpected(self, expectation)

        self._check_line_matcher_type(
            utils.single_line_source(),
            ARBITRARY_MODEL,
            _constant_line_matcher_type_parser_of_matcher_sdv(sdv_that_checks_symbols),
            sut.Arrangement(
                symbols=symbol_table_of_arrangement),
            sut.Expectation(),
        )


class TestHardError(TestCaseBase):
    def test_expected_hard_error_is_detected(self):
        parser_that_gives_value_that_causes_hard_error = _constant_line_matcher_type_parser_of_matcher(
            matchers.MatcherThatReportsHardError()
        )
        self._check_line_matcher_type(
            utils.single_line_source(),
            ARBITRARY_MODEL,
            parser_that_gives_value_that_causes_hard_error,
            sut.Arrangement(),
            sut.Expectation(
                is_hard_error=is_hard_error(),
            ))

    def test_missing_hard_error_is_detected(self):
        with self.assertRaises(utils.TestError):
            self._check_line_matcher_type(
                utils.single_line_source(),
                ARBITRARY_MODEL,
                PARSER_THAT_GIVES_MATCHER_THAT_MATCHES_WO_SYMBOL_REFS_AND_SUCCESSFUL_VALIDATION,
                sut.Arrangement(),
                sut.Expectation(
                    is_hard_error=is_hard_error(),
                ))


class TestTypes(TestCaseBase):
    def test_expect_given_logic_value_type(self):
        with self.assertRaises(utils.TestError):
            sut.check(
                self.tc,
                utils.single_line_source(),
                ARBITRARY_MODEL_CONSTRUCTOR,
                PARSER_THAT_GIVES_MATCHER_THAT_MATCHES_WO_SYMBOL_REFS_AND_SUCCESSFUL_VALIDATION,
                sut.Arrangement(),
                UNEXPECTED_LOGIC_TYPE_FOR_TEST,
                EXPECTED_VALUE_TYPE_FOR_TEST,
                sut.Expectation(),
            )

    def test_expect_given_value_type(self):
        with self.assertRaises(utils.TestError):
            sut.check(
                self.tc,
                utils.single_line_source(),
                ARBITRARY_MODEL_CONSTRUCTOR,
                PARSER_THAT_GIVES_MATCHER_THAT_MATCHES_WO_SYMBOL_REFS_AND_SUCCESSFUL_VALIDATION,
                sut.Arrangement(),
                EXPECTED_LOGIC_TYPE_FOR_TEST,
                UNEXPECTED_VALUE_TYPE_FOR_TEST,
                sut.Expectation(),
            )


class TestDefault(TestCaseBase):

    def test_expect_no_symbol_usages(self):
        with self.assertRaises(utils.TestError):
            unexpected_symbol_usages = [data_symbol_utils.symbol_reference('symbol_name')]
            self._check_line_matcher_type(
                utils.single_line_source(),
                ARBITRARY_MODEL,
                _constant_line_matcher_type_parser_of_matcher_sdv(
                    matchers.sdv_from_primitive_value(references=unexpected_symbol_usages)
                ),
                sut.Arrangement(),
                sut.Expectation(),
            )

    def test_expect_pre_validation_succeeds(self):
        with self.assertRaises(utils.TestError):
            self._check_line_matcher_type(utils.single_line_source(),
                                          ARBITRARY_MODEL,
                                          _constant_line_matcher_type_parser_of_matcher_ddv(
                                              matchers.MatcherDdvOfConstantMatcherTestImpl(
                                                  matchers.MatcherWithConstantResult(True),
                                                  ConstantDdvValidator(
                                                      pre_sds_result=rend_comb.ConstantSequenceR([])
                                                  )
                                              )
                                          ),
                                          sut.Arrangement(),
                                          Expectation(),
                                          )

    def test_expect_post_validation_succeeds(self):
        with self.assertRaises(utils.TestError):
            self._check_line_matcher_type(utils.single_line_source(),
                                          ARBITRARY_MODEL,
                                          _constant_line_matcher_type_parser_of_matcher_ddv(
                                              matchers.MatcherDdvOfConstantMatcherTestImpl(
                                                  matchers.MatcherWithConstantResult(True),
                                                  ConstantDdvValidator(
                                                      post_sds_result=rend_comb.ConstantSequenceR([])
                                                  )
                                              )
                                          ),
                                          sut.Arrangement(),
                                          Expectation(),
                                          )

    def test_expects_no_hard_error(self):
        parser_that_gives_value_that_causes_hard_error = _constant_line_matcher_type_parser_of_matcher_sdv(
            matchers.sdv_from_primitive_value(MatcherThatReportsHardError())
        )
        with self.assertRaises(utils.TestError):
            self._check_line_matcher_type(
                utils.single_line_source(),
                ARBITRARY_MODEL,
                parser_that_gives_value_that_causes_hard_error,
                sut.Arrangement(),
                sut.Expectation(),
            )

    def test_expect_match_is_true(self):
        with self.assertRaises(utils.TestError):
            self._check_line_matcher_type(
                utils.single_line_source(),
                ARBITRARY_MODEL,
                _constant_line_matcher_type_parser_of_matcher_sdv(
                    matchers.sdv_from_primitive_value(
                        matchers.MatcherWithConstantResult(False)
                    )
                ),
                sut.Arrangement(),
                sut.Expectation())

    def test_successful_flow(self):
        self._check_line_matcher_type(
            utils.single_line_source(),
            ARBITRARY_MODEL,
            PARSER_THAT_GIVES_MATCHER_THAT_MATCHES_WO_SYMBOL_REFS_AND_SUCCESSFUL_VALIDATION,
            sut.Arrangement(),
            sut.Expectation())

    def test_tcds_directories_are_empty(self):
        all_tcds_dirs_are_empty = asrt.and_([
            dir_is_empty(tcds_dir)
            for tcds_dir in RelOptionType
        ])

        self._check_line_matcher_type(
            utils.single_line_source(),
            ARBITRARY_MODEL,
            parser_of_matcher_that_is_an_assertion_on_tcds(
                self,
                all_tcds_dirs_are_empty,
            ),
            sut.Arrangement(),
            sut.Expectation())


class TestFailingExpectations(TestCaseBase):
    def test_fail_due_to_unexpected_result_from_pre_validation(self):
        with self.assertRaises(utils.TestError):
            self._check_line_matcher_type(utils.single_line_source(),
                                          ARBITRARY_MODEL,
                                          ConstantParser(_MATCHER_THAT_MATCHES),
                                          sut.Arrangement(),
                                          Expectation(
                                              validation=asrt_validation.pre_sds_validation_fails(),
                                          )
                                          )

    def test_fail_due_to_unexpected_result_from_post_validation(self):
        with self.assertRaises(utils.TestError):
            self._check_line_matcher_type(utils.single_line_source(),
                                          ARBITRARY_MODEL,
                                          ConstantParser(_MATCHER_THAT_MATCHES),
                                          sut.Arrangement(),
                                          Expectation(
                                              validation=asrt_validation.post_sds_validation_fails(),
                                          )
                                          )

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(utils.TestError):
            self._check_line_matcher_type(
                utils.single_line_source(),
                ARBITRARY_MODEL,
                ConstantParser(_MATCHER_THAT_MATCHES),
                sut.Arrangement(),
                Expectation(
                    main_result=matcher_assertions.is_arbitrary_matching_failure()),
            )


class TestPopulateDirectoriesAndCwd(TestCaseBase):
    def test_that_cwd_for_main_and_post_validation_is_test_root(self):
        def make_primitive(tcds: Tcds) -> MatcherWTraceAndNegation[int]:
            return MatcherThatAssertsThatCwdIsIsActDir(self, tcds)

        self._check_line_matcher_type(
            utils.single_line_source(),
            ARBITRARY_MODEL,
            _constant_line_matcher_type_parser_of_matcher_ddv(
                matchers.MatcherDdvFromPartsTestImpl(
                    make_primitive,
                    ValidatorThatAssertsThatCwdIsIsActDirAtPostSdsValidation(self),
                )
            ),
            sut.Arrangement(),
            Expectation())

    def test_populate_hds(self):
        populated_dir_contents = DirContents([empty_file('hds-file.txt')])
        the_hds_dir = RelHdsOptionType.REL_HDS_CASE
        self._check_line_matcher_type(
            utils.single_line_source(),
            ARBITRARY_MODEL,
            parser_of_matcher_that_is_an_assertion_on_tcds(
                self,
                hds_contents_check.hds_2_tcds_assertion(
                    hds_contents_check.dir_contains_exactly(the_hds_dir,
                                                            populated_dir_contents)
                )
            ),
            sut.Arrangement(
                hds_contents=hds_populators.contents_in(
                    the_hds_dir,
                    populated_dir_contents)),
            Expectation(),
        )

    def test_populate_non_hds(self):
        populated_dir_contents = DirContents([empty_file('non-home-file.txt')])
        self._check_line_matcher_type(
            utils.single_line_source(),
            ARBITRARY_MODEL,
            parser_of_matcher_that_is_an_assertion_on_tcds(
                self,
                sds_2_tcds_assertion(
                    tmp_user_dir_contains_exactly(populated_dir_contents)
                )
            ),
            sut.Arrangement(
                non_hds_contents=non_hds_populator.rel_option(
                    non_hds_populator.RelNonHdsOptionType.REL_TMP,
                    populated_dir_contents)),
            Expectation(),
        )

    def test_populate_result_dir_with_act_result(self):
        act_result = SubProcessResult(
            exitcode=72,
            stdout='the stdout',
            stderr='the stderr',
        )

        result_dir_contains_files_corresponding_to_act_result = asrt_tcds_contents.dir_contains_exactly(
            RelOptionType.REL_RESULT,
            DirContents([
                File(sds.RESULT_FILE__EXITCODE, str(act_result.exitcode)),
                File(sds.RESULT_FILE__STDOUT, str(act_result.stdout)),
                File(sds.RESULT_FILE__STDERR, str(act_result.stderr)),
            ])
        )

        all_tcds_dirs_but_result_dir_are_empty = asrt.and_([
            dir_is_empty(tcds_dir)
            for tcds_dir in RelOptionType if tcds_dir is not RelOptionType.REL_RESULT
        ])

        self._check_line_matcher_type(
            utils.single_line_source(),
            ARBITRARY_MODEL,
            parser_of_matcher_that_is_an_assertion_on_tcds(
                self,
                asrt.and_([
                    result_dir_contains_files_corresponding_to_act_result,
                    all_tcds_dirs_but_result_dir_are_empty,
                ]
                )
            ),
            sut.Arrangement(
                act_result=ActResultProducerFromActResult(act_result)
            ),
            Expectation(),
        )


class _MatcherTypeSdvTestImpl(MatcherTypeSdv[int]):
    def __init__(self,
                 matcher: MatcherSdv[int],
                 ):
        self._matcher = matcher

    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.LINE_MATCHER

    @property
    def value_type(self) -> ValueType:
        return ValueType.LINE_MATCHER

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._matcher.references

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[int]:
        return self._matcher.resolve(symbols)


class MatcherSdvThatAssertsThatSymbolsAreAsExpected(MatcherSdv[int]):
    def __init__(self,
                 put: unittest.TestCase,
                 expectation: ValueAssertion[SymbolTable]):
        self._put = put
        self._expectation = expectation

    @property
    def references(self) -> List[SymbolReference]:
        return []

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[int]:
        self._expectation.apply_with_message(self._put, symbols, 'symbols given to resolve')

        return matchers.ddv_of_unconditionally_matching_matcher()


def _line_matcher_type_sdv(matcher: MatcherSdv[int]) -> MatcherTypeSdv[int]:
    return _MatcherTypeSdvTestImpl(matcher)


def _constant_line_matcher_type_parser_of_matcher_sdv(matcher: MatcherSdv[int]) -> Parser[MatcherTypeSdv[int]]:
    return ConstantParser(_line_matcher_type_sdv(matcher))


def _constant_line_matcher_type_parser_of_matcher_ddv(matcher: MatcherDdv[int]) -> Parser[MatcherTypeSdv[int]]:
    return ConstantParser(_line_matcher_type_sdv(matchers.MatcherSdvOfConstantDdvTestImpl(matcher)))


def _constant_line_matcher_type_parser_of_matcher(matcher: MatcherWTraceAndNegation[int]
                                                  ) -> Parser[MatcherTypeSdv[int]]:
    return ConstantParser(_line_matcher_type_sdv(matchers.sdv_from_primitive_value(matcher)))


ARBITRARY_MODEL = 0
ARBITRARY_MODEL_CONSTRUCTOR = sut.constant_model(ARBITRARY_MODEL)

PARSER_THAT_GIVES_MATCHER_THAT_MATCHES_WO_SYMBOL_REFS_AND_SUCCESSFUL_VALIDATION = \
    _constant_line_matcher_type_parser_of_matcher_sdv(
        matchers.sdv_from_primitive_value()
    )

_MATCHER_THAT_MATCHES = _line_matcher_type_sdv(matchers.sdv_from_primitive_value())


def dir_is_empty(tcds_dir: RelOptionType) -> ValueAssertion[Tcds]:
    return asrt.sub_component(str(tcds_dir),
                              REL_OPTIONS_MAP[tcds_dir].root_resolver.from_tcds,
                              file_assertions.dir_is_empty())


def parser_of_matcher_that_is_an_assertion_on_tcds(put: unittest.TestCase,
                                                   assertion: ValueAssertion[Tcds],
                                                   ) -> Parser[MatcherTypeSdv[int]]:
    return _constant_line_matcher_type_parser_of_matcher_ddv(
        _MatcherDdvThatIsAssertionOnTcds(put, assertion)
    )


class ValidatorThatAssertsThatCwdIsIsActDirAtPostSdsValidation(DdvValidator):
    def __init__(self, put: unittest.TestCase):
        self._put = put

    def validate_pre_sds_if_applicable(self, hds: HomeDirectoryStructure) -> Optional[TextRenderer]:
        return None

    def validate_post_sds_if_applicable(self, tcds: Tcds) -> Optional[TextRenderer]:
        cwd = pathlib.Path.cwd()
        self._put.assertEqual(cwd, tcds.sds.act_dir, 'current directory at validation post-sds')
        return None


class MatcherThatAssertsThatCwdIsIsActDir(MatcherWTraceAndNegation[int]):
    def __init__(self,
                 put: unittest.TestCase,
                 tcds: Tcds,
                 ):
        self._put = put
        self._tcds = tcds

    @property
    def negation(self) -> MatcherWTraceAndNegation[int]:
        raise NotImplementedError('unsupported')

    def matches_w_failure(self, model: MODEL) -> Optional[Failure[MODEL]]:
        raise NotImplementedError('unsupported')

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        cwd = pathlib.Path.cwd()
        self._put.assertEqual(cwd, self._tcds.sds.act_dir, 'current directory at matcher application')
        return TraceBuilder(self.name).build_result(True)

    @property
    def name(self) -> str:
        return str(type(self))

    def matches_emr(self, model: MODEL) -> Optional[ErrorMessageResolver]:
        raise NotImplementedError('unsupported')

    @property
    def option_description(self) -> str:
        return self.name


class _MatcherDdvThatIsAssertionOnTcds(MatcherDdv[int]):
    MATCHER = constant.MatcherWithConstantResult(True)

    def __init__(self,
                 put: unittest.TestCase,
                 assertion: ValueAssertion[Tcds],
                 ):
        self._put = put
        self._assertion = assertion

    def structure(self) -> StructureRenderer:
        return self.MATCHER.structure()

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        self._assertion.apply_with_message(self._put, tcds, 'assertion on tcds')
        return advs.ConstantAdv(self.MATCHER)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
