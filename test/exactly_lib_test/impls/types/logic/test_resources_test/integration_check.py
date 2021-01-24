import pathlib
import unittest
from typing import List, Optional, Generic, Callable

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.impls.types.matcher.impls import constant
from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import Parser, ParserFromTokenParserBase
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.value_type import ValueType, LogicValueType
from exactly_lib.tcfs import sds as sds
from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.path_relativity import RelHdsOptionType, RelOptionType
from exactly_lib.tcfs.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv import advs
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import ConstantDdvValidator, DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.dep_variants.sdv.matcher import MatcherSdv
from exactly_lib.type_val_deps.envs.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_prims.description.trace_building import TraceBuilder
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.matcher_base_class import MODEL, \
    MatcherWTrace
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.impls.types.logic.test_resources import integration_check as sut
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import ParseExpectation, ExecutionExpectation, \
    Expectation, TcdsArrangement, Arrangement, arrangement_wo_tcds, arrangement_w_tcds, prim_asrt__constant, \
    adv_asrt__constant
from exactly_lib_test.impls.types.matcher.test_resources import matchers
from exactly_lib_test.impls.types.matcher.test_resources import sdv_ddv
from exactly_lib_test.impls.types.matcher.test_resources.integration_check import constant_model
from exactly_lib_test.impls.types.matcher.test_resources.integration_check import \
    is_expectation_of_execution_result_of
from exactly_lib_test.impls.types.matcher.test_resources.matcher_checker import \
    MatcherPropertiesConfiguration
from exactly_lib_test.impls.types.matcher.test_resources.matchers import MatcherThatReportsHardError, \
    MatcherTestImplBase
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.impls.types.test_resources import matcher_assertions
from exactly_lib_test.section_document.test_resources.parser_classes import ConstantParser
from exactly_lib_test.tcfs.test_resources import non_hds_populator, hds_contents_check, \
    hds_populators
from exactly_lib_test.tcfs.test_resources import tcds_contents_assertions as asrt_tcds_contents
from exactly_lib_test.tcfs.test_resources.sds_check.sds_contents_check import \
    tmp_user_dir_contains_exactly
from exactly_lib_test.test_case.test_resources import test_of_test_framework_utils as utils
from exactly_lib_test.test_case.test_resources.act_result import ActResultProducerFromActResult
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import sds_2_tcds_assertion
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt, file_assertions
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_deps.data.test_resources import data_symbol_utils, \
    symbol_structure_assertions as asrt_sym
from exactly_lib_test.type_val_deps.data.test_resources import symbol_reference_assertions as sym_asrt
from exactly_lib_test.type_val_deps.dep_variants.test_resources.full_deps.sdv_checker import \
    WithNodeDescriptionExecutionPropertiesChecker
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestDefault),
        unittest.makeSuite(TestFailingCommonProperties),
        unittest.makeSuite(TestFailingExpectations),
        unittest.makeSuite(TestSymbolReferences),
        unittest.makeSuite(TestHardError),
        unittest.makeSuite(TestPopulateDirectoriesAndCwd),
    ])


EXPECTED_LOGIC_TYPE_FOR_TEST = LogicValueType.LINE_MATCHER
UNEXPECTED_LOGIC_TYPE_FOR_TEST = LogicValueType.FILE_MATCHER

CONFIGURATION = MatcherPropertiesConfiguration()


class _CustomMatcherPropertiesConfiguration(MatcherPropertiesConfiguration):
    def __init__(self, application_output: ValueAssertion[MatchingResult]):
        super().__init__()
        self._application_output = application_output

    def new_execution_checker(self) -> WithNodeDescriptionExecutionPropertiesChecker[MatchingResult]:
        return WithNodeDescriptionExecutionPropertiesChecker(
            MatcherDdv,
            MatcherWTrace,
            self._application_output,
        )


EXPECTED_VALUE_TYPE_FOR_TEST = ValueType.LINE_MATCHER
UNEXPECTED_VALUE_TYPE_FOR_TEST = ValueType.FILE_MATCHER

_EMPTY_ARRANGEMENT_W_WO_TCDS = [
    NameAndValue('without tcds', Arrangement()),
    NameAndValue('with tcds', Arrangement(
        tcds=TcdsArrangement()))
]

IntegrationCheckerForTest = sut.IntegrationChecker[
    MatcherWTrace[int],
    Callable[[FullResolvingEnvironment], int],
    MatchingResult
]


def _application_result_check_cases(parser: Parser[MatcherSdv[int]],
                                    ) -> List[NameAndValue[IntegrationCheckerForTest]]:
    return [
        NameAndValue(
            'check_application_result_with_tcds:False',
            sut.IntegrationChecker(parser, CONFIGURATION, False),
        ),
        NameAndValue(
            'check_application_result_with_tcds:True',
            sut.IntegrationChecker(parser, CONFIGURATION, True),
        ),
    ]


class TestCaseBase(unittest.TestCase):
    def setUp(self):
        self.tc = utils.TestCaseWithTestErrorAsFailureException()

    def _check(self,
               source: ParseSource,
               model: int,
               checker: IntegrationCheckerForTest,
               arrangement: Arrangement,
               expectation: Expectation,
               ):
        checker.check(self.tc,
                      source,
                      constant_model(model),
                      arrangement,
                      expectation,
                      )

    def _check___multi(self,
                       arguments: Arguments,
                       model: int,
                       checker: IntegrationCheckerForTest,
                       arrangement: Arrangement,
                       expectation: Expectation):
        checker.check_single_multi_execution_setup__for_test_of_test_resources(
            self.tc,
            arguments,
            expectation.parse,
            constant_model(model),
            NExArr('only execution',
                   expectation.prim_and_exe,
                   arrangement),
        )

    def _check___single_and_multi(self,
                                  arguments: Arguments,
                                  model: int,
                                  parser: Parser[MatcherSdv[int]],
                                  arrangement: Arrangement,
                                  expectation: Expectation):
        for case in _application_result_check_cases(parser):
            with self.subTest(case.name):
                with self.subTest('single execution'):
                    case.value.check(
                        self.tc,
                        arguments.as_remaining_source,
                        constant_model(model),
                        arrangement, expectation,
                    )
                with self.subTest('multiple executions'):
                    case.value.check_single_multi_execution_setup__for_test_of_test_resources(
                        self.tc,
                        arguments,
                        expectation.parse,
                        constant_model(model),
                        NExArr('the one and only execution',
                               expectation.prim_and_exe,
                               arrangement),
                    )

    def _check_raises_test_error__single_and_multi(self,
                                                   parser: Parser[MatcherSdv[int]],
                                                   expectation: Expectation,
                                                   ):
        for check_application_result_with_tcds in [False, True]:
            checker = sut.IntegrationChecker(parser, CONFIGURATION, check_application_result_with_tcds)
            for arrangement in _EMPTY_ARRANGEMENT_W_WO_TCDS:
                with self.subTest(arrangement.name,
                                  check_application_result_with_tcds=check_application_result_with_tcds,
                                  execution_variant='single execution'):
                    with self.assertRaises(utils.TestError):
                        self._check(
                            utils.single_line_source(),
                            ARBITRARY_MODEL,
                            checker,
                            arrangement.value,
                            expectation,
                        )

                with self.subTest(arrangement.name,
                                  check_application_result_with_tcds=check_application_result_with_tcds,
                                  execution_variant='multiple execution'):
                    with self.assertRaises(utils.TestError):
                        self._check___multi(
                            utils.single_line_arguments(),
                            ARBITRARY_MODEL,
                            checker,
                            arrangement.value,
                            expectation,
                        )


class TestSymbolReferences(TestCaseBase):
    def test_that_fails_due_to_missing_symbol_reference(self):
        symbol_usages_of_matcher = []
        symbol_usages_of_expectation = [data_symbol_utils.symbol_reference('symbol_name')]

        self._check_raises_test_error__single_and_multi(
            _constant_line_matcher_type_parser_of_matcher_sdv(
                sdv_ddv.sdv_from_primitive_value(references=symbol_usages_of_matcher)
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=sym_asrt.equals_data_type_symbol_references(symbol_usages_of_expectation)
                ),
            )
        )

    def test_that_symbols_from_arrangement_exist_in_environment(self):
        symbol = StringConstantSymbolContext('symbol_name', 'the symbol value')
        symbol_table_of_arrangement = symbol.symbol_table
        expected_symbol_table = symbol.symbol_table
        expectation = asrt_sym.equals_symbol_table(expected_symbol_table)

        sdv_that_checks_symbols = MatcherSdvThatAssertsThatSymbolsAreAsExpected(self, expectation)

        cases = [
            NameAndValue('arrangement without tcds',
                         arrangement_wo_tcds(
                             symbol_table_of_arrangement)
                         ),
            NameAndValue('arrangement with tcds',
                         arrangement_w_tcds(
                             symbols=symbol_table_of_arrangement)
                         ),
        ]
        for arrangement in cases:
            with self.subTest(arrangement.name):
                self._check___single_and_multi(
                    utils.single_line_arguments(),
                    ARBITRARY_MODEL,
                    _constant_line_matcher_type_parser_of_matcher_sdv(sdv_that_checks_symbols),
                    arrangement.value,
                    Expectation(),
                )


class TestHardError(TestCaseBase):
    def test_expected_hard_error_is_detected(self):
        parser_that_gives_value_that_causes_hard_error = _constant_line_matcher_type_parser_of_matcher(
            matchers.MatcherThatReportsHardError()
        )
        for arrangement in _EMPTY_ARRANGEMENT_W_WO_TCDS:
            with self.subTest(arrangement.name):
                self._check___single_and_multi(
                    utils.single_line_arguments(),
                    ARBITRARY_MODEL,
                    parser_that_gives_value_that_causes_hard_error,
                    arrangement.value,
                    Expectation(
                        execution=ExecutionExpectation(
                            is_hard_error=matcher_assertions.is_hard_error(),
                        ),
                    ),
                )

    def test_missing_hard_error_is_detected(self):
        self._check_raises_test_error__single_and_multi(
            PARSER_THAT_GIVES_MATCHER_THAT_MATCHES_WO_SYMBOL_REFS_AND_SUCCESSFUL_VALIDATION,
            Expectation(
                execution=ExecutionExpectation(
                    is_hard_error=matcher_assertions.is_hard_error(),
                ),
            )
        )


class TestDefault(TestCaseBase):
    def test_expect_no_symbol_usages(self):
        self._check_raises_test_error__single_and_multi(
            _constant_line_matcher_type_parser_of_matcher_sdv(
                sdv_ddv.sdv_from_primitive_value(
                    references=[data_symbol_utils.symbol_reference('symbol_name')])
            ),
            is_expectation_of_execution_result_of(True),
        )

    def test_expect_pre_validation_succeeds(self):
        self._check_raises_test_error__single_and_multi(
            _constant_line_matcher_type_parser_of_matcher_ddv(
                sdv_ddv.MatcherDdvOfConstantMatcherTestImpl(
                    constant.MatcherWithConstantResult(True),
                    ConstantDdvValidator(
                        pre_sds_result=rend_comb.ConstantSequenceR(
                            [])))
            ),
            is_expectation_of_execution_result_of(True),
        )

    def test_expect_post_validation_succeeds(self):
        self._check_raises_test_error__single_and_multi(
            _constant_line_matcher_type_parser_of_matcher_ddv(
                sdv_ddv.MatcherDdvOfConstantMatcherTestImpl(
                    constant.MatcherWithConstantResult(True),
                    ConstantDdvValidator(
                        post_sds_result=rend_comb.ConstantSequenceR([])))
            ),
            is_expectation_of_execution_result_of(True),
        )

    def test_expects_no_hard_error(self):
        parser_that_gives_value_that_causes_hard_error = _constant_line_matcher_type_parser_of_matcher_sdv(
            sdv_ddv.sdv_from_primitive_value(MatcherThatReportsHardError())
        )
        self._check_raises_test_error__single_and_multi(
            parser_that_gives_value_that_causes_hard_error,
            is_expectation_of_execution_result_of(True),
        )

    def test_expect_match_is_true(self):
        self._check_raises_test_error__single_and_multi(
            _constant_line_matcher_type_parser_of_matcher_sdv(
                sdv_ddv.sdv_from_primitive_value(constant.MatcherWithConstantResult(False))
            ),
            is_expectation_of_execution_result_of(True),
        )

    def test_successful_flow(self):
        for arrangement in _EMPTY_ARRANGEMENT_W_WO_TCDS:
            with self.subTest(arrangement.name):
                self._check___single_and_multi(
                    utils.single_line_arguments(),
                    ARBITRARY_MODEL,
                    PARSER_THAT_GIVES_MATCHER_THAT_MATCHES_WO_SYMBOL_REFS_AND_SUCCESSFUL_VALIDATION,
                    arrangement.value,
                    is_expectation_of_execution_result_of(True),
                )

    def test_tcds_directories_are_empty(self):
        all_tcds_dirs_are_empty = asrt.and_([
            dir_is_empty(tcds_dir)
            for tcds_dir in RelOptionType
        ])

        self._check___single_and_multi(
            utils.single_line_arguments(),
            ARBITRARY_MODEL,
            parser_of_matcher_that_is_an_assertion_on_tcds(
                self,
                all_tcds_dirs_are_empty,
            ),
            arrangement_w_tcds(),
            is_expectation_of_execution_result_of(True))


class TestFailingCommonProperties(TestCaseBase):
    def test_fail_due_to_unsatisfied_assertion_on_output_from_application(self):
        matcher_result_value = True
        for check_application_result_with_tcds in [False, True]:
            parser = _constant_line_matcher_type_parser_of_matcher_sdv(
                sdv_ddv.sdv_from_primitive_value(constant.MatcherWithConstantResult(matcher_result_value))
            )
            checker = sut.IntegrationChecker(
                parser,
                _CustomMatcherPropertiesConfiguration(asrt_matching_result.matches_value(not matcher_result_value)),
                check_application_result_with_tcds,
            )

            expectation = is_expectation_of_execution_result_of(matcher_result_value)
            for arrangement in _EMPTY_ARRANGEMENT_W_WO_TCDS:
                with self.subTest(arrangement.name,
                                  check_application_result_with_tcds=check_application_result_with_tcds,
                                  execution_variant='single execution'):
                    with self.assertRaises(utils.TestError):
                        self._check(
                            utils.single_line_source(),
                            ARBITRARY_MODEL,
                            checker,
                            arrangement.value,
                            expectation,
                        )

                with self.subTest(arrangement.name,
                                  check_application_result_with_tcds=check_application_result_with_tcds,
                                  execution_variant='multiple execution'):
                    with self.assertRaises(utils.TestError):
                        self._check___multi(
                            utils.single_line_arguments(),
                            ARBITRARY_MODEL,
                            checker,
                            arrangement.value,
                            expectation,
                        )


class TestFailingExpectations(TestCaseBase):
    def test_fail_due_to_unexpected_result_from_pre_validation(self):
        self._check_raises_test_error__single_and_multi(
            ConstantParser(_MATCHER_THAT_MATCHES),
            Expectation(
                execution=ExecutionExpectation(
                    validation=ValidationAssertions.pre_sds_fails(),
                ),
            )
        )

    def test_fail_due_to_unexpected_result_from_post_sds_validation(self):
        self._check_raises_test_error__single_and_multi(
            ConstantParser(_MATCHER_THAT_MATCHES),
            Expectation(
                execution=ExecutionExpectation(
                    validation=ValidationAssertions.post_sds_fails(),
                ),
            )
        )

    def test_fail_due_to_unsatisfied_assertion_on_adv(self):
        self._check_raises_test_error__single_and_multi(
            ConstantParser(_MATCHER_THAT_MATCHES),
            Expectation(
                execution=ExecutionExpectation(),
                adv=adv_asrt__constant(asrt.fail('adv'))
            ),
        )

    def test_fail_due_to_unsatisfied_assertion_on_primitive(self):
        self._check_raises_test_error__single_and_multi(
            ConstantParser(_MATCHER_THAT_MATCHES),
            Expectation(
                execution=ExecutionExpectation(),
                primitive=prim_asrt__constant(asrt.fail('primitive'))
            ),
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
        def make_primitive(tcds: TestCaseDs) -> MatcherWTrace[int]:
            return constant.MatcherWithConstantResult(True)

        self._check___single_and_multi(
            utils.single_line_arguments(),
            ARBITRARY_MODEL,
            _constant_line_matcher_type_parser_of_matcher_ddv(
                sdv_ddv.MatcherDdvFromPartsTestImpl(
                    make_primitive,
                    ValidatorThatAssertsThatTcdsDirsDoesNotDenoteExistingDirectories(self),
                )
            ),
            arrangement_wo_tcds(),
            Expectation(),
        )

    def test_that_cwd_for_main_and_post_validation_is_test_root(self):
        def make_primitive(tcds: TestCaseDs) -> MatcherWTrace[int]:
            return MatcherThatAssertsThatCwdIsIsActDir(self, tcds)

        self._check___single_and_multi(
            utils.single_line_arguments(),
            ARBITRARY_MODEL,
            _constant_line_matcher_type_parser_of_matcher_ddv(
                sdv_ddv.MatcherDdvFromPartsTestImpl(
                    make_primitive,
                    ValidatorThatAssertsThatCwdIsIsActDirAtPostSdsValidation(self),
                )
            ),
            arrangement_w_tcds(),
            Expectation())

    def test_populate_hds(self):
        populated_dir_contents = DirContents([File.empty('hds-file.txt')])
        the_hds_dir = RelHdsOptionType.REL_HDS_CASE
        self._check___single_and_multi(
            utils.single_line_arguments(),
            ARBITRARY_MODEL,
            parser_of_matcher_that_is_an_assertion_on_tcds(
                self,
                hds_contents_check.hds_2_tcds_assertion(
                    hds_contents_check.dir_contains_exactly(the_hds_dir,
                                                            populated_dir_contents)
                )
            ),
            arrangement_w_tcds(
                hds_contents=hds_populators.contents_in(
                    the_hds_dir,
                    populated_dir_contents)),
            Expectation(),
        )

    def test_populate_non_hds(self):
        populated_dir_contents = DirContents([File.empty('non-home-file.txt')])
        self._check___single_and_multi(
            utils.single_line_arguments(),
            ARBITRARY_MODEL,
            parser_of_matcher_that_is_an_assertion_on_tcds(
                self,
                sds_2_tcds_assertion(
                    tmp_user_dir_contains_exactly(populated_dir_contents)
                )
            ),
            arrangement_w_tcds(
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

        self._check___single_and_multi(
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
            arrangement_w_tcds(
                act_result=ActResultProducerFromActResult(act_result)
            ),
            Expectation(),
        )


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

        return sdv_ddv.ddv_of_unconditionally_matching_matcher()


class _ConstantParserOfSingleTokenExpression(ParserFromTokenParserBase[MatcherSdv[int]]):
    def __init__(self, constant_result: MatcherSdv[int]):
        super().__init__()
        self._constant_result = constant_result

    def parse_from_token_parser(self, parser: TokenParser) -> MatcherSdv[int]:
        parser.consume_mandatory_token('expecting single arbitrary token')
        return self._constant_result


def _constant_line_matcher_type_parser_of_matcher_sdv(matcher: MatcherSdv[int]) -> Parser[MatcherSdv[int]]:
    return _ConstantParserOfSingleTokenExpression(matcher)


def _constant_line_matcher_type_parser_of_matcher_ddv(matcher: MatcherDdv[int]) -> Parser[MatcherSdv[int]]:
    return _ConstantParserOfSingleTokenExpression(
        sdv_ddv.MatcherSdvOfConstantDdvTestImpl(matcher))


def _constant_line_matcher_type_parser_of_matcher(matcher: MatcherWTrace[int]
                                                  ) -> Parser[MatcherSdv[int]]:
    return _ConstantParserOfSingleTokenExpression(
        sdv_ddv.sdv_from_primitive_value(matcher))


ARBITRARY_MODEL = 0
ARBITRARY_MODEL_CONSTRUCTOR = constant_model(ARBITRARY_MODEL)

PARSER_THAT_GIVES_MATCHER_THAT_MATCHES_WO_SYMBOL_REFS_AND_SUCCESSFUL_VALIDATION = \
    _constant_line_matcher_type_parser_of_matcher_sdv(
        sdv_ddv.sdv_from_primitive_value()
    )

_MATCHER_THAT_MATCHES = sdv_ddv.sdv_from_primitive_value()


def dir_is_empty(tcds_dir: RelOptionType) -> ValueAssertion[TestCaseDs]:
    return asrt.sub_component(str(tcds_dir),
                              REL_OPTIONS_MAP[tcds_dir].root_resolver.from_tcds,
                              file_assertions.dir_is_empty())


def parser_of_matcher_that_is_an_assertion_on_tcds(put: unittest.TestCase,
                                                   assertion: ValueAssertion[TestCaseDs],
                                                   ) -> Parser[MatcherSdv[int]]:
    return _constant_line_matcher_type_parser_of_matcher_ddv(
        _MatcherDdvThatIsAssertionOnTcds(put, assertion)
    )


class ValidatorThatAssertsThatCwdIsIsActDirAtPostSdsValidation(DdvValidator):
    def __init__(self, put: unittest.TestCase):
        self._put = put

    def validate_pre_sds_if_applicable(self, hds: HomeDs) -> Optional[TextRenderer]:
        return None

    def validate_post_sds_if_applicable(self, tcds: TestCaseDs) -> Optional[TextRenderer]:
        cwd = pathlib.Path.cwd()
        self._put.assertEqual(cwd, tcds.sds.act_dir, 'current directory at validation post-sds')
        return None


class ValidatorThatAssertsThatTcdsDirsDoesNotDenoteExistingDirectories(DdvValidator):
    def __init__(self, put: unittest.TestCase):
        self._put = put

    def validate_pre_sds_if_applicable(self, hds: HomeDs) -> Optional[TextRenderer]:
        self._put.assertFalse(hds.case_dir.exists())
        self._put.assertFalse(hds.act_dir.exists())
        return None

    def validate_post_sds_if_applicable(self, tcds: TestCaseDs) -> Optional[TextRenderer]:
        self._put.assertFalse(tcds.sds.root_dir.exists())
        return None


class MatcherThatAssertsThatCwdIsIsActDir(MatcherTestImplBase[int]):
    def __init__(self,
                 put: unittest.TestCase,
                 tcds: TestCaseDs,
                 ):
        self._put = put
        self._tcds = tcds

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
                 assertion: ValueAssertion[TestCaseDs],
                 ):
        self._put = put
        self._assertion = assertion

    def structure(self) -> StructureRenderer:
        return self.MATCHER.structure()

    def value_of_any_dependency(self, tcds: TestCaseDs) -> MatcherAdv[MODEL]:
        self._assertion.apply_with_message(self._put, tcds, 'assertion on tcds')
        return advs.ConstantMatcherAdv(self.MATCHER)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
