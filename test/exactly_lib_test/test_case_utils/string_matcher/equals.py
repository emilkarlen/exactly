import unittest

from exactly_lib.symbol.data.restrictions.reference_restrictions import is_any_data_type
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.string_matcher.parse.parts.equality import \
    EXPECTED_FILE_REL_OPT_ARG_CONFIG
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.string import lines_content
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources import parse_source_assertions  as asrt_source
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer, \
    StringTransformerSymbolContext
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import Expectation, \
    ExecutionExpectation, ParseExpectation
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import arrangement_w_tcds
from exactly_lib_test.test_case_utils.string_matcher.test_resources import contents_transformation, integration_check, \
    test_configuration
from exactly_lib_test.test_case_utils.string_matcher.test_resources.arguments_building import args
from exactly_lib_test.test_case_utils.string_matcher.test_resources.expectation_utils import \
    expectation_that_file_for_expected_contents_is_invalid
from exactly_lib_test.test_case_utils.string_matcher.test_resources.misc import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_case_utils.string_matcher.test_resources.relativity_options import \
    suite_for__rel_opts__negations, RelativityOptionConfigurationForRelCwdForTestCwdDir, \
    TestWithRelativityOptionAndNegationBase
from exactly_lib_test.test_case_utils.string_matcher.test_resources.test_configuration import \
    TestWithNegationArgumentBase
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForNoneIsSuccess
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir, File
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
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
            integration_check.empty_model(),
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
            integration_check.empty_model(),
            arrangement_w_tcds(
                tcds_contents=self.rel_opt.populator_for_relativity_option_root(
                    DirContents([empty_dir('dir')])),
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
            integration_check.model_of('actual'),
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
            integration_check.model_of('expected'),
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


class _ContentsEqualsAHereDocument(TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        self._check(
            test_configuration.source_for(
                args('{maybe_not} {equals} <<EOF',
                     maybe_not=maybe_not.nothing__if_positive__not_option__if_negative),
                ['expected content line',
                 'EOF']),
            integration_check.model_of(lines_content(['expected content line'])),
            arrangement_w_tcds(
                post_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY),
            Expectation(
                ParseExpectation(
                    source=asrt_source.source_is_at_end,
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
            integration_check.model_of(expected_contents),
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

        symbol = NameAndValue('symbol_name', 'the symbol value')
        self._check(
            test_configuration.source_for(
                args('{maybe_not} {equals} <<EOF',
                     maybe_not=maybe_not.nothing__if_positive__not_option__if_negative),
                [expected_content(symbol_reference_syntax_for_name(symbol.name)),
                 'EOF',
                 'following line']),
            integration_check.model_of(lines_content([expected_content(symbol.value)])),
            arrangement_w_tcds(
                post_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=SymbolTable({
                    symbol.name: data_symbol_utils.string_constant_container(symbol.value),
                })),
            Expectation(
                ParseExpectation(
                    source=asrt_source.is_at_beginning_of_line(4),
                    symbol_references=equals_symbol_references([
                        SymbolReference(symbol.name, is_any_data_type())
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
            integration_check.model_of(lines_content(['actual contents that is not equal to expected contents'])),
            arrangement_w_tcds(
                post_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY),
            Expectation(
                ParseExpectation(
                    source=asrt_source.is_at_beginning_of_line(4)
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
            contents_transformation.ToUppercaseStringTransformer()
        )

        contents_generator = contents_transformation.TransformedContentsSetup(
            original='some\ntext',
            transformed='SOME\nTEXT',
        )

        symbols = self.rel_opt.symbols.in_arrangement()
        symbols.put(named_transformer.name,
                    named_transformer.symbol_table_container)

        expected_symbol_reference_to_transformer = is_reference_to_string_transformer(named_transformer.name)

        expected_symbol_usages = asrt.matches_sequence(
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
            integration_check.model_of(contents_generator.original),
            arrangement_w_tcds(
                tcds_contents=self.rel_opt.populator_for_relativity_option_root(DirContents([
                    File('expected.txt', contents_generator.transformed)
                ])),
                post_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=symbols,
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=expected_symbol_usages,
                ),
                ExecutionExpectation(
                    main_result=self.not_opt.pass__if_positive__fail__if_negative,
                ),
            ),
        )
