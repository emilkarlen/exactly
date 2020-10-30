import pathlib
import unittest
from abc import ABC
from typing import Sequence

from exactly_lib.appl_env.application_environment import ApplicationEnvironment
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.test_case_utils.string_matcher.parse.equality import \
    EXPECTED_FILE_REL_OPT_ARG_CONFIG
from exactly_lib.type_system.logic.string_matcher import StringMatcherSdv
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.section_document.test_resources import parse_source_assertions  as asrt_source
from exactly_lib_test.symbol.logic.test_resources.string_transformer.assertions import \
    is_reference_to_string_transformer
from exactly_lib_test.symbol.logic.test_resources.string_transformer.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.symbol.test_resources.string import StringConstantSymbolContext, StringSymbolContext
from exactly_lib_test.tcfs.test_resources.paths import fake_tcds
from exactly_lib_test.tcfs.test_resources.sub_dir_of_sds_act import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ParseExpectation, \
    ExecutionExpectation, Expectation
from exactly_lib_test.test_case_utils.string_matcher.test_resources import arguments_building2 as args2
from exactly_lib_test.test_case_utils.string_matcher.test_resources import contents_transformation, test_configuration
from exactly_lib_test.test_case_utils.string_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.string_matcher.test_resources.arguments_building import args
from exactly_lib_test.test_case_utils.string_matcher.test_resources.expectation_utils import \
    expectation_that_file_for_expected_contents_is_invalid
from exactly_lib_test.test_case_utils.string_matcher.test_resources.relativity_options import \
    suite_for__rel_opts__negations, RelativityOptionConfigurationForRelCwdForTestCwdDir, \
    TestWithRelativityOptionAndNegationBase
from exactly_lib_test.test_case_utils.string_matcher.test_resources.test_configuration import \
    TestWithNegationArgumentBase
from exactly_lib_test.test_case_utils.string_models.test_resources import model_constructor
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForNoneIsSuccess
from exactly_lib_test.test_resources.files.file_structure import DirContents, File, Dir
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir
from exactly_lib_test.test_resources.test_utils import ArrEx
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_transformer.test_resources import string_transformers
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result
from exactly_lib_test.util.file_utils.test_resources.tmp_file_spaces import TmpFileSpaceThatAllowsSinglePathGeneration
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes_str


def suite() -> unittest.TestSuite:
    test_cases_for_rel_opts = [
        _ErrorWhenExpectedFileDoesNotExist,
        _ErrorWhenExpectedFileIsADirectory,
        _ContentsDiffer,
        _ContentsEquals,

        _WhenStringTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents,
    ]

    suite_with_negation = unittest.TestSuite([
        _ContentsEqualsAHereDocument(),
        _ContentsEqualsAString(),
        _ContentsEqualsAHereDocumentWithSymbolReferences(),
        _ContentsDoNotEqualAHereDocument(),
    ])

    return unittest.TestSuite([
        suite_for__rel_opts__negations(_RELATIVITY_OPTION_CONFIGURATIONS_FOR_EXPECTED_FILE,
                                       test_cases_for_rel_opts),
        suite_with_negation,
        _TestEqualsString(),
        _TestEqualsFile(),
        _TestWhenMultipleInvocationsForModelWExtDepsThenPathForExpectedMustBeCreatedOnlyOnce(),
    ])


_RELATIVITY_OPTION_CONFIGURATIONS_FOR_EXPECTED_FILE = [
    rel_opt.conf_rel_any(RelOptionType.REL_HDS_CASE),
    RelativityOptionConfigurationForRelCwdForTestCwdDir(),
    rel_opt.conf_rel_any(RelOptionType.REL_ACT),
    rel_opt.conf_rel_any(RelOptionType.REL_TMP),
    rel_opt.default_conf_rel_any(RelOptionType.REL_HDS_CASE),
    rel_opt.symbol_conf_rel_any(RelOptionType.REL_TMP,
                                'EXPECTED_FILE_SYMBOL',
                                EXPECTED_FILE_REL_OPT_ARG_CONFIG.options.accepted_relativity_variants),
    rel_opt.symbol_conf_rel_any(RelOptionType.REL_HDS_CASE,
                                'EXPECTED_FILE_SYMBOL',
                                EXPECTED_FILE_REL_OPT_ARG_CONFIG.options.accepted_relativity_variants),
]

_TRANSFORMER_SYMBOL_NAME = 'the_transformer'


class _ErrorWhenExpectedFileDoesNotExist(TestWithRelativityOptionAndNegationBase):
    def runTest(self):
        self._check_with_source_variants(
            test_configuration.arguments_for(
                args('{maybe_not} {equals} {file_option} {relativity_option} non-existing-file.txt',
                     maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                     relativity_option=self.rel_opt.option_argument)),
            model_constructor.empty(self),
            arrangement_w_tcds(
                post_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            expectation_that_file_for_expected_contents_is_invalid(self.rel_opt),
        )


class _ErrorWhenExpectedFileIsADirectory(TestWithRelativityOptionAndNegationBase):
    def runTest(self):
        self._check_with_source_variants(
            test_configuration.arguments_for(
                args('{maybe_not} {equals} {file_option} {relativity_option} dir',
                     maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                     relativity_option=self.rel_opt.option_argument)),
            model_constructor.empty(self),
            arrangement_w_tcds(
                tcds_contents=self.rel_opt.populator_for_relativity_option_root(
                    DirContents([Dir.empty('dir')])),
                post_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            expectation_that_file_for_expected_contents_is_invalid(self.rel_opt),
        )


class _ContentsDiffer(TestWithRelativityOptionAndNegationBase):
    def runTest(self):
        self._check_with_source_variants(
            test_configuration.arguments_for(
                args('{maybe_not} {equals} {file_option} {relativity_option} expected.txt',
                     maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                     relativity_option=self.rel_opt.option_argument)),
            model_constructor.of_str(self, 'actual'),
            arrangement_w_tcds(
                self.rel_opt.populator_for_relativity_option_root(
                    DirContents([File('expected.txt', 'expected')])),
                post_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=self.rel_opt.symbols.usages_expectation(),
                ),
                ExecutionExpectation(
                    main_result=self.not_opt.fail__if_positive__pass_if_negative,
                ),
            ),
        )


class _ContentsEquals(TestWithRelativityOptionAndNegationBase):
    def runTest(self):
        self._check_with_source_variants(
            test_configuration.arguments_for(
                args('{maybe_not} {equals} {file_option} {relativity_option} expected.txt',
                     maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                     relativity_option=self.rel_opt.option_argument)),
            model_constructor.of_str(self, 'expected'),
            arrangement_w_tcds(
                self.rel_opt.populator_for_relativity_option_root(
                    DirContents([File('expected.txt', 'expected')])),
                post_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=self.rel_opt.symbols.usages_expectation(),
                ),
                ExecutionExpectation(
                    main_result=self.not_opt.pass__if_positive__fail__if_negative,
                ),
            ),
        )


class _TestEqualsWSourceVariantsBase(unittest.TestCase, ABC):
    def runTest(self):
        for case in contents_cases():
            for may_depend_on_external_resources in [False, True]:
                for actual_case in case.as_actual_expected_sequence():
                    expected_result = case.expected == actual_case.arrangement
                    with self.subTest(expected_case=case.name,
                                      may_depend_on_external_resources=may_depend_on_external_resources,
                                      expected_contents=case.expected,
                                      actual_contents=actual_case.arrangement,
                                      expected_result=expected_result):
                        self._check(
                            case.expected,
                            actual_case.arrangement,
                            may_depend_on_external_resources,
                            expected_result,
                        )

    def _check(self,
               expected_contents: str,
               actual_contents: str,
               may_depend_on_external_resources: bool,
               expected_result: bool,
               ):
        pass


class _TestEqualsString(_TestEqualsWSourceVariantsBase):
    def _check(self,
               expected_contents: str,
               actual_contents: str,
               may_depend_on_external_resources: bool,
               expected_result: bool,
               ):
        string_symbol_with_expected = StringSymbolContext.of_constant(
            'EXPECTED_CONTENTS_SYMBOL',
            expected_contents,
        )
        integration_check.CHECKER__PARSE_SIMPLE.check(
            self,
            args2.Equals.eq_string(
                string_symbol_with_expected.name__sym_ref_syntax
            ).as_remaining_source,
            model_constructor.of_str(
                self,
                actual_contents,
                may_depend_on_external_resources=may_depend_on_external_resources,
            ),
            arrangement_w_tcds(
                symbols=string_symbol_with_expected.symbol_table
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_singleton_sequence(
                        string_symbol_with_expected.reference_assertion__any_data_type
                    )
                ),
                execution=ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(
                        expected_result
                    )
                ),
            ),
        )


class _TestEqualsFile(_TestEqualsWSourceVariantsBase):
    def _check(self,
               expected_contents: str,
               actual_contents: str,
               may_depend_on_external_resources: bool,
               expected_result: bool,
               ):
        expected_file_relativity = rel_opt.conf_rel_any(RelOptionType.REL_HDS_CASE)
        expected_contents_file = File('expected.txt', expected_contents)
        integration_check.CHECKER__PARSE_SIMPLE.check(
            self,
            args2.Equals.eq_file(
                expected_file_relativity.path_argument_of_rel_name(expected_contents_file.name)
            ).as_remaining_source,
            model_constructor.of_str(self, actual_contents,
                                     may_depend_on_external_resources=may_depend_on_external_resources),
            arrangement_w_tcds(
                tcds_contents=expected_file_relativity.populator_for_relativity_option_root(
                    DirContents([expected_contents_file])
                )
            ),
            Expectation(
                execution=ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(
                        expected_result
                    )
                ),
            ),
        )


class _ContentsEqualsAHereDocument(TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        self._check(
            test_configuration.source_for(
                args('{maybe_not} {equals} <<EOF',
                     maybe_not=maybe_not.nothing__if_positive__not_option__if_negative),
                ['expected content line',
                 'EOF']),
            model_constructor.of_str(self, lines_content(['expected content line'])),
            arrangement_w_tcds(
                post_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY),
            Expectation(
                ParseExpectation(
                    source=asrt_source.is_at_end_of_line(3),
                ),
                ExecutionExpectation(
                    main_result=maybe_not.pass__if_positive__fail__if_negative,
                ),
            ),
        )


class _ContentsEqualsAString(TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        expected_contents = 'expected contents'
        self._check_with_source_variants(
            test_configuration.arguments_for(
                args('{maybe_not} {equals} {expected_contents}',
                     expected_contents=surrounded_by_hard_quotes_str(expected_contents),
                     maybe_not=maybe_not.nothing__if_positive__not_option__if_negative),
            ),
            model_constructor.of_str(self, expected_contents),
            arrangement_w_tcds(
                post_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY),
            Expectation(
                execution=ExecutionExpectation(
                    main_result=maybe_not.pass__if_positive__fail__if_negative
                ),
            ),
        )


class _ContentsEqualsAHereDocumentWithSymbolReferences(TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        expected_content_line_template = 'expected content line, with {symbol} ref'

        def expected_content(symbol_content: str) -> str:
            return expected_content_line_template.format(symbol=symbol_content)

        symbol = StringConstantSymbolContext('symbol_name', 'the symbol value')
        self._check(
            test_configuration.source_for(
                args('{maybe_not} {equals} <<EOF',
                     maybe_not=maybe_not.nothing__if_positive__not_option__if_negative),
                [expected_content(symbol.name__sym_ref_syntax),
                 'EOF',
                 'following line']),
            model_constructor.of_str(self, lines_content([expected_content(symbol.str_value)])),
            arrangement_w_tcds(
                post_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=symbol.symbol_table),
            Expectation(
                ParseExpectation(
                    source=asrt_source.is_at_end_of_line(3),
                    symbol_references=asrt.matches_sequence([
                        symbol.reference_assertion__any_data_type
                    ]),
                ),
                ExecutionExpectation(
                    main_result=maybe_not.pass__if_positive__fail__if_negative,
                ),
            ),
        )


class _ContentsDoNotEqualAHereDocument(TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        self._check(
            test_configuration.source_for(
                args('{maybe_not} {equals} <<EOF',
                     maybe_not=maybe_not.nothing__if_positive__not_option__if_negative),
                ['expected content line',
                 'EOF',
                 'the following line']),
            model_constructor.of_lines_wo_nl(self, ['actual contents that is not equal to expected contents']),
            arrangement_w_tcds(
                post_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY),
            Expectation(
                ParseExpectation(
                    source=asrt_source.is_at_end_of_line(3)
                ),
                ExecutionExpectation(
                    main_result=maybe_not.fail__if_positive__pass_if_negative,
                ),
            ),
        )


class _WhenStringTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents(
    TestWithRelativityOptionAndNegationBase):
    def runTest(self):
        # ARRANGE #
        named_transformer = StringTransformerSymbolContext.of_primitive(
            _TRANSFORMER_SYMBOL_NAME,
            string_transformers.to_uppercase()
        )

        contents_generator = contents_transformation.TransformedContentsSetup(
            original='some\ntext',
            transformed='SOME\nTEXT',
        )

        symbols = self.rel_opt.symbols.in_arrangement()
        symbols.put(named_transformer.name,
                    named_transformer.symbol_table_container)

        expected_symbol_reference_to_transformer = is_reference_to_string_transformer(named_transformer.name)

        expected_symbol_references = asrt.matches_sequence(
            [expected_symbol_reference_to_transformer] +
            self.rel_opt.symbols.usage_expectation_assertions()
        )
        self._check_with_source_variants(
            test_configuration.arguments_for(
                args(
                    '{transform_option} {transformer} {maybe_not} {equals} '
                    '{file_option} {relativity_option} expected.txt',
                    transformer=named_transformer.name,
                    maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                    relativity_option=self.rel_opt.option_argument)),
            model_constructor.of_str(self, contents_generator.original),
            arrangement_w_tcds(
                tcds_contents=self.rel_opt.populator_for_relativity_option_root(DirContents([
                    File('expected.txt', contents_generator.transformed)
                ])),
                post_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=symbols,
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=expected_symbol_references,
                ),
                ExecutionExpectation(
                    main_result=self.not_opt.pass__if_positive__fail__if_negative,
                ),
            ),
        )


class _TestWhenMultipleInvocationsForModelWExtDepsThenPathForExpectedMustBeCreatedOnlyOnce(unittest.TestCase):
    proc_exe_arr = ProcessExecutionArrangement()

    def runTest(self):
        expected_contents = 'expected-contents'
        resolving_env = PathResolvingEnvironmentPreOrPostSds(fake_tcds())

        sdv = self._sdv_expecting_equals(expected_contents)
        adv = sdv.resolve(resolving_env.symbols).value_of_any_dependency(resolving_env.tcds)

        for actual_contents in [expected_contents, expected_contents + '-unexpected']:
            expected_result = actual_contents == expected_contents
            expected_matching_result = asrt_matching_result.matches_value(expected_result)
            with self.subTest(expected_result=expected_result):
                model_w_ext_deps = model_constructor.of_str(
                    self,
                    actual_contents,
                    may_depend_on_external_resources=True,
                )
                with tmp_dir() as dir_space_dir__matcher:
                    matcher = adv.primitive(self._app_env(dir_space_dir__matcher, 'matcher-path'))
                    with tmp_dir() as dir_space_dir__model:
                        model = model_w_ext_deps(FullResolvingEnvironment(
                            resolving_env.symbols,
                            resolving_env.tcds,
                            self._app_env(dir_space_dir__model, 'model-path')
                        ))
                        # ACT #
                        matching_result_1st = matcher.matches_w_trace(model)
                        matching_result_2nd = matcher.matches_w_trace(model)
                        # ASSERT #
                        expected_matching_result.apply_with_message(self, matching_result_1st, '1st')
                        expected_matching_result.apply_with_message(self, matching_result_2nd, '2nd')

    def _app_env(self,
                 dir_space_dir: pathlib.Path,
                 path_name_prefix: str,
                 ) -> ApplicationEnvironment:
        dir_file_space__matcher = TmpFileSpaceThatAllowsSinglePathGeneration(
            self,
            dir_space_dir,
            path_name_prefix,
        )
        return ApplicationEnvironment(
            self.proc_exe_arr.os_services,
            self.proc_exe_arr.process_execution_settings,
            dir_file_space__matcher,
        )

    @staticmethod
    def _sdv_expecting_equals(expected_contents: str) -> StringMatcherSdv:
        source = args2.Equals.eq_string(expected_contents).as_remaining_source
        return integration_check.CHECKER__PARSE_SIMPLE.parser.parse(source)


class Case:
    def __init__(self,
                 name: str,
                 expected: str,
                 unexpected: Sequence[str],
                 ):
        self.name = name
        self.expected = expected
        self.unexpected = unexpected

    def as_actual_expected_sequence(self) -> Sequence[ArrEx[str, bool]]:
        return (
                [ArrEx(self.expected, True)] +
                [
                    ArrEx(unexpected, False)
                    for unexpected in self.unexpected
                ]
        )


def contents_cases() -> Sequence[Case]:
    return [
        Case(
            'expected empty',
            '',
            [
                'non empty',
                '\nfollowing line'
            ],
        ),
        Case(
            'expected single line wo new-line',
            'expected',
            [
                'exp',
                'expected followed by more on same line',
                'expected\nfollowed by more on following line',
                'expected\n',
            ]
        ),
        Case(
            'expected single line w new-line',
            'expected\n',
            [
                'exp',
                'expected\nfollowed by more on following line',
            ]
        ),
        Case(
            'multiple lines',
            '1\n2\n',
            [
                '1\n2',
                '1\n2\n3',
                '1\n2\n3\n',
                '0\n1\n2\n',
            ]
        ),
    ]
