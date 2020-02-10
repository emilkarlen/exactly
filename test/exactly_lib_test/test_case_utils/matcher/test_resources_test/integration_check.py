import pathlib
import unittest
from typing import List, Sequence, Optional, Generic

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.logic_type_sdv import MatcherTypeSdv
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case.validation.ddv_validation import ConstantDdvValidator, DdvValidator
from exactly_lib.test_case_file_structure import sandbox_directory_structure as sds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import RelHdsOptionType, RelOptionType
from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.impls import advs
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherWTraceAndNegation, MODEL, \
    MatchingResult, MatcherAdv
from exactly_lib.type_system.value_type import ValueType, LogicValueType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources.parser_classes import ConstantParser
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils, symbol_reference_assertions as sym_asrt
from exactly_lib_test.symbol.data.test_resources import symbol_structure_assertions as asrt_sym
from exactly_lib_test.test_case.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.test_case.test_resources.act_result import ActResultProducerFromActResult
from exactly_lib_test.test_case_file_structure.test_resources import non_hds_populator, hds_contents_check, \
    hds_populators
from exactly_lib_test.test_case_file_structure.test_resources import tcds_contents_assertions as asrt_tcds_contents
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    tmp_user_dir_contains_exactly
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers, integration_check as sut
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import Expectation, ExecutionExpectation, \
    ParseExpectation
from exactly_lib_test.test_case_utils.matcher.test_resources.matchers import MatcherThatReportsHardError, \
    MatcherTestImplBase
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.test_resources import matcher_assertions
from exactly_lib_test.test_case_utils.test_resources import validation as asrt_validation
from exactly_lib_test.test_resources.files.file_structure import empty_file, DirContents, File
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import sds_2_tcds_assertion
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt, file_assertions
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestDefault))
    ret_val.addTest(unittest.makeSuite(TestTypes))
    ret_val.addTest(unittest.makeSuite(TestFailingExpectations))
    ret_val.addTest(unittest.makeSuite(TestSymbolReferences))
    ret_val.addTest(unittest.makeSuite(TestHardError))
    ret_val.addTest(unittest.makeSuite(TestPopulateDirectoriesAndCwd))
    return ret_val


EXPECTED_LOGIC_TYPE_FOR_TEST = LogicValueType.LINE_MATCHER
UNEXPECTED_LOGIC_TYPE_FOR_TEST = LogicValueType.FILE_MATCHER

EXPECTED_VALUE_TYPE_FOR_TEST = ValueType.LINE_MATCHER
UNEXPECTED_VALUE_TYPE_FOR_TEST = ValueType.FILE_MATCHER

_EMPTY_ARRANGEMENT_W_WO_TCDS = [
    NameAndValue('without tcds', sut.Arrangement()),
    NameAndValue('with tcds', sut.Arrangement(tcds=sut.TcdsArrangement()))
]


class TestCaseBase(unittest.TestCase):
    def setUp(self):
        self.tc = utils.TestCaseWithTestErrorAsFailureException()

    def _check_line_matcher_type(self,
                                 source: ParseSource,
                                 model: int,
                                 parser: Parser[MatcherTypeSdv[int]],
                                 arrangement: sut.arrangement_w_tcds,
                                 expectation: sut.Expectation):
        checker = sut.MatcherChecker(parser, EXPECTED_LOGIC_TYPE_FOR_TEST)
        checker.check(self.tc,
                      source,
                      sut.constant_model(model),
                      arrangement, expectation)

    def _check_line_matcher_type__multi(self,
                                        arguments: Arguments,
                                        model: int,
                                        parser: Parser[MatcherTypeSdv[int]],
                                        arrangement: sut.arrangement_w_tcds,
                                        expectation: sut.Expectation):
        checker = sut.MatcherChecker(parser, EXPECTED_LOGIC_TYPE_FOR_TEST)
        checker.check_single_multi_execution_setup__for_test_of_test_resources(
            self.tc,
            arguments,
            expectation.parse,
            sut.constant_model(model),
            NExArr('only execution',
                   expectation.execution,
                   arrangement),
        )

    def _check_line_matcher_type__single_and_multi(self,
                                                   arguments: Arguments,
                                                   model: int,
                                                   parser: Parser[MatcherTypeSdv[int]],
                                                   arrangement: sut.arrangement_w_tcds,
                                                   expectation: sut.Expectation):
        checker = sut.MatcherChecker(parser, EXPECTED_LOGIC_TYPE_FOR_TEST)
        with self.subTest('single execution'):
            checker.check(self.tc,
                          arguments.as_remaining_source,
                          sut.constant_model(model),
                          arrangement, expectation)
        with self.subTest('multiple executions'):
            checker.check_single_multi_execution_setup__for_test_of_test_resources(
                self.tc,
                arguments,
                expectation.parse,
                sut.constant_model(model),
                NExArr('the one and only execution',
                       expectation.execution,
                       arrangement),
            )

    def _check_raises_test_error__single_and_multi(self,
                                                   parser: Parser[MatcherTypeSdv[int]],
                                                   expectation: sut.Expectation,
                                                   ):
        for arrangement in _EMPTY_ARRANGEMENT_W_WO_TCDS:
            with self.subTest(arrangement.name,
                              execution_variant='single execution'):
                with self.assertRaises(utils.TestError):
                    self._check_line_matcher_type(
                        utils.single_line_source(),
                        ARBITRARY_MODEL,
                        parser,
                        arrangement.value,
                        expectation,
                    )

            with self.subTest(arrangement.name,
                              execution_variant='multiple execution'):
                with self.assertRaises(utils.TestError):
                    self._check_line_matcher_type__multi(
                        utils.single_line_arguments(),
                        ARBITRARY_MODEL,
                        parser,
                        arrangement.value,
                        expectation,
                    )


class TestSymbolReferences(TestCaseBase):
    def test_that_fails_due_to_missing_symbol_reference(self):
        symbol_usages_of_matcher = []
        symbol_usages_of_expectation = [data_symbol_utils.symbol_reference('symbol_name')]

        self._check_raises_test_error__single_and_multi(
            _constant_line_matcher_type_parser_of_matcher_sdv(
                matchers.sdv_from_primitive_value(references=symbol_usages_of_matcher)
            ),
            sut.Expectation(
                ParseExpectation(
                    symbol_references=sym_asrt.equals_symbol_references(symbol_usages_of_expectation)
                ),
            )
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

        cases = [
            NameAndValue('arrangement without tcds',
                         sut.arrangement_wo_tcds(symbol_table_of_arrangement)
                         ),
            NameAndValue('arrangement with tcds',
                         sut.arrangement_w_tcds(symbols=symbol_table_of_arrangement)
                         ),
        ]
        for arrangement in cases:
            with self.subTest(arrangement.name):
                self._check_line_matcher_type__single_and_multi(
                    utils.single_line_arguments(),
                    ARBITRARY_MODEL,
                    _constant_line_matcher_type_parser_of_matcher_sdv(sdv_that_checks_symbols),
                    arrangement.value,
                    sut.Expectation(),
                )


class TestHardError(TestCaseBase):
    def test_expected_hard_error_is_detected(self):
        parser_that_gives_value_that_causes_hard_error = _constant_line_matcher_type_parser_of_matcher(
            matchers.MatcherThatReportsHardError()
        )
        for arrangement in _EMPTY_ARRANGEMENT_W_WO_TCDS:
            with self.subTest(arrangement.name):
                self._check_line_matcher_type__single_and_multi(
                    utils.single_line_arguments(),
                    ARBITRARY_MODEL,
                    parser_that_gives_value_that_causes_hard_error,
                    arrangement.value,
                    sut.Expectation(
                        execution=ExecutionExpectation(
                            is_hard_error=matcher_assertions.is_hard_error(),
                        ),
                    ),
                )

    def test_missing_hard_error_is_detected(self):
        self._check_raises_test_error__single_and_multi(
            PARSER_THAT_GIVES_MATCHER_THAT_MATCHES_WO_SYMBOL_REFS_AND_SUCCESSFUL_VALIDATION,
            sut.Expectation(
                execution=ExecutionExpectation(
                    is_hard_error=matcher_assertions.is_hard_error(),
                ),
            )
        )


class TestTypes(TestCaseBase):
    def test_expect_given_logic_value_type(self):
        checker = sut.MatcherChecker(PARSER_THAT_GIVES_MATCHER_THAT_MATCHES_WO_SYMBOL_REFS_AND_SUCCESSFUL_VALIDATION,
                                     UNEXPECTED_LOGIC_TYPE_FOR_TEST)
        expectation = sut.Expectation()
        for arrangement in _EMPTY_ARRANGEMENT_W_WO_TCDS:
            with self.subTest(arrangement.name,
                              execution_variant='single execution'):
                with self.assertRaises(utils.TestError):
                    checker.check(self.tc,
                                  utils.single_line_source(),
                                  ARBITRARY_MODEL_CONSTRUCTOR,
                                  arrangement.value,
                                  expectation)

            with self.subTest(arrangement.name,
                              execution_variant='multiple execution'):
                with self.assertRaises(utils.TestError):
                    checker.check_single_multi_execution_setup__for_test_of_test_resources(
                        self.tc,
                        utils.single_line_arguments(),
                        expectation.parse,
                        ARBITRARY_MODEL_CONSTRUCTOR,
                        NExArr('the one and only execution',
                               expectation.execution,
                               arrangement.value),
                    )


class TestDefault(TestCaseBase):
    def test_expect_no_symbol_usages(self):
        self._check_raises_test_error__single_and_multi(
            _constant_line_matcher_type_parser_of_matcher_sdv(
                matchers.sdv_from_primitive_value(
                    references=[data_symbol_utils.symbol_reference('symbol_name')])
            ),
            sut.Expectation(),
        )

    def test_expect_pre_validation_succeeds(self):
        self._check_raises_test_error__single_and_multi(
            _constant_line_matcher_type_parser_of_matcher_ddv(
                matchers.MatcherDdvOfConstantMatcherTestImpl(
                    matchers.MatcherWithConstantResult(True),
                    ConstantDdvValidator(
                        pre_sds_result=rend_comb.ConstantSequenceR(
                            [])))
            ),
            sut.Expectation(),
        )

    def test_expect_post_validation_succeeds(self):
        self._check_raises_test_error__single_and_multi(
            _constant_line_matcher_type_parser_of_matcher_ddv(
                matchers.MatcherDdvOfConstantMatcherTestImpl(
                    matchers.MatcherWithConstantResult(True),
                    ConstantDdvValidator(
                        post_sds_result=rend_comb.ConstantSequenceR([])))
            ),
            sut.Expectation(),
        )

    def test_expects_no_hard_error(self):
        parser_that_gives_value_that_causes_hard_error = _constant_line_matcher_type_parser_of_matcher_sdv(
            matchers.sdv_from_primitive_value(MatcherThatReportsHardError())
        )
        self._check_raises_test_error__single_and_multi(
            parser_that_gives_value_that_causes_hard_error,
            sut.Expectation(),
        )

    def test_expect_match_is_true(self):
        self._check_raises_test_error__single_and_multi(
            _constant_line_matcher_type_parser_of_matcher_sdv(
                matchers.sdv_from_primitive_value(matchers.MatcherWithConstantResult(False))
            ),
            sut.Expectation(),
        )

    def test_successful_flow(self):
        for arrangement in _EMPTY_ARRANGEMENT_W_WO_TCDS:
            with self.subTest(arrangement.name):
                self._check_line_matcher_type__single_and_multi(
                    utils.single_line_arguments(),
                    ARBITRARY_MODEL,
                    PARSER_THAT_GIVES_MATCHER_THAT_MATCHES_WO_SYMBOL_REFS_AND_SUCCESSFUL_VALIDATION,
                    arrangement.value,
                    sut.Expectation(),
                )

    def test_tcds_directories_are_empty(self):
        all_tcds_dirs_are_empty = asrt.and_([
            dir_is_empty(tcds_dir)
            for tcds_dir in RelOptionType
        ])

        self._check_line_matcher_type__single_and_multi(
            utils.single_line_arguments(),
            ARBITRARY_MODEL,
            parser_of_matcher_that_is_an_assertion_on_tcds(
                self,
                all_tcds_dirs_are_empty,
            ),
            sut.arrangement_w_tcds(),
            sut.Expectation())


class TestFailingExpectations(TestCaseBase):
    def test_fail_due_to_unexpected_result_from_pre_validation(self):
        self._check_raises_test_error__single_and_multi(
            ConstantParser(_MATCHER_THAT_MATCHES),
            Expectation(
                execution=ExecutionExpectation(
                    validation=asrt_validation.pre_sds_validation_fails(),
                ),
            )
        )

    def test_fail_due_to_unexpected_result_from_post_sds_validation(self):
        self._check_raises_test_error__single_and_multi(
            ConstantParser(_MATCHER_THAT_MATCHES),
            Expectation(
                execution=ExecutionExpectation(
                    validation=asrt_validation.post_sds_validation_fails(),
                ),
            )
        )

    def test_fail_due_to_unexpected_result_from_main(self):
        self._check_raises_test_error__single_and_multi(
            ConstantParser(_MATCHER_THAT_MATCHES),
            Expectation(
                execution=ExecutionExpectation(
                    main_result=matcher_assertions.is_arbitrary_matching_failure()
                ),
            ),
        )


class TestPopulateDirectoriesAndCwd(TestCaseBase):
    def test_tcds_SHOULD_not_exist_WHEN_flag_for_not_creating_tcds_is_given(self):
        def make_primitive(tcds: Tcds) -> MatcherWTraceAndNegation[int]:
            return matchers.MatcherWithConstantResult(True)

        self._check_line_matcher_type__single_and_multi(
            utils.single_line_arguments(),
            ARBITRARY_MODEL,
            _constant_line_matcher_type_parser_of_matcher_ddv(
                matchers.MatcherDdvFromPartsTestImpl(
                    make_primitive,
                    ValidatorThatAssertsThatTcdsDirsDoesNotDenoteExistingDirectories(self),
                )
            ),
            sut.arrangement_wo_tcds(),
            sut.Expectation(),
        )

    def test_that_cwd_for_main_and_post_validation_is_test_root(self):
        def make_primitive(tcds: Tcds) -> MatcherWTraceAndNegation[int]:
            return MatcherThatAssertsThatCwdIsIsActDir(self, tcds)

        self._check_line_matcher_type__single_and_multi(
            utils.single_line_arguments(),
            ARBITRARY_MODEL,
            _constant_line_matcher_type_parser_of_matcher_ddv(
                matchers.MatcherDdvFromPartsTestImpl(
                    make_primitive,
                    ValidatorThatAssertsThatCwdIsIsActDirAtPostSdsValidation(self),
                )
            ),
            sut.arrangement_w_tcds(),
            sut.Expectation())

    def test_populate_hds(self):
        populated_dir_contents = DirContents([empty_file('hds-file.txt')])
        the_hds_dir = RelHdsOptionType.REL_HDS_CASE
        self._check_line_matcher_type__single_and_multi(
            utils.single_line_arguments(),
            ARBITRARY_MODEL,
            parser_of_matcher_that_is_an_assertion_on_tcds(
                self,
                hds_contents_check.hds_2_tcds_assertion(
                    hds_contents_check.dir_contains_exactly(the_hds_dir,
                                                            populated_dir_contents)
                )
            ),
            sut.arrangement_w_tcds(
                hds_contents=hds_populators.contents_in(
                    the_hds_dir,
                    populated_dir_contents)),
            sut.Expectation(),
        )

    def test_populate_non_hds(self):
        populated_dir_contents = DirContents([empty_file('non-home-file.txt')])
        self._check_line_matcher_type__single_and_multi(
            utils.single_line_arguments(),
            ARBITRARY_MODEL,
            parser_of_matcher_that_is_an_assertion_on_tcds(
                self,
                sds_2_tcds_assertion(
                    tmp_user_dir_contains_exactly(populated_dir_contents)
                )
            ),
            sut.arrangement_w_tcds(
                non_hds_contents=non_hds_populator.rel_option(
                    non_hds_populator.RelNonHdsOptionType.REL_TMP,
                    populated_dir_contents)),
            sut.Expectation(),
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

        self._check_line_matcher_type__single_and_multi(
            utils.single_line_arguments(),
            ARBITRARY_MODEL,
            parser_of_matcher_that_is_an_assertion_on_tcds(
                self,
                asrt.and_([
                    result_dir_contains_files_corresponding_to_act_result,
                    all_tcds_dirs_but_result_dir_are_empty,
                ]
                )
            ),
            sut.arrangement_w_tcds(
                act_result=ActResultProducerFromActResult(act_result)
            ),
            sut.Expectation(),
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


class MatcherSdvThatAssertsThatSymbolsAreAsExpected(Generic[MODEL], MatcherSdv[MODEL]):
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


class _ConstantParserOfSingleTokenExpression(Parser[MatcherTypeSdv[int]]):
    def __init__(self, constant_result: MatcherTypeSdv[int]):
        super().__init__()
        self._constant_result = constant_result

    def parse_from_token_parser(self, parser: TokenParser) -> MatcherTypeSdv[int]:
        parser.consume_mandatory_token('expecting single arbitrary token')
        return self._constant_result


def _constant_line_matcher_type_parser_of_matcher_sdv(matcher: MatcherSdv[int]) -> Parser[MatcherTypeSdv[int]]:
    return _ConstantParserOfSingleTokenExpression(_line_matcher_type_sdv(matcher))


def _constant_line_matcher_type_parser_of_matcher_ddv(matcher: MatcherDdv[int]) -> Parser[MatcherTypeSdv[int]]:
    return _ConstantParserOfSingleTokenExpression(
        _line_matcher_type_sdv(matchers.MatcherSdvOfConstantDdvTestImpl(matcher)))


def _constant_line_matcher_type_parser_of_matcher(matcher: MatcherWTraceAndNegation[int]
                                                  ) -> Parser[MatcherTypeSdv[int]]:
    return _ConstantParserOfSingleTokenExpression(_line_matcher_type_sdv(matchers.sdv_from_primitive_value(matcher)))


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


class ValidatorThatAssertsThatTcdsDirsDoesNotDenoteExistingDirectories(DdvValidator):
    def __init__(self, put: unittest.TestCase):
        self._put = put

    def validate_pre_sds_if_applicable(self, hds: HomeDirectoryStructure) -> Optional[TextRenderer]:
        self._put.assertFalse(hds.case_dir.exists())
        self._put.assertFalse(hds.act_dir.exists())
        return None

    def validate_post_sds_if_applicable(self, tcds: Tcds) -> Optional[TextRenderer]:
        self._put.assertFalse(tcds.sds.root_dir.exists())
        return None


class MatcherThatAssertsThatCwdIsIsActDir(MatcherTestImplBase[int]):
    def __init__(self,
                 put: unittest.TestCase,
                 tcds: Tcds,
                 ):
        self._put = put
        self._tcds = tcds

    @property
    def negation(self) -> MatcherWTraceAndNegation[int]:
        raise NotImplementedError('unsupported')

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        cwd = pathlib.Path.cwd()
        self._put.assertEqual(cwd, self._tcds.sds.act_dir, 'current directory at matcher application')
        return TraceBuilder(self.name).build_result(True)

    @property
    def name(self) -> str:
        return str(type(self))


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
        return advs.ConstantMatcherAdv(self.MATCHER)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
