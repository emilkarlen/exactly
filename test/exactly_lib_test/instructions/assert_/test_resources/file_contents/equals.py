import unittest

from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.test_case_utils.string_matcher.parse.equality import \
    EXPECTED_FILE_REL_OPT_ARG_CONFIG
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals, TestWithConfigurationAndNegationArgumentBase, \
    suite_for__conf__not_argument
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    suite_for__conf__rel_opts__negations, RelativityOptionConfigurationForRelCwdForTestCwdDir, \
    TestWithConfigurationAndRelativityOptionAndNegationBase
from exactly_lib_test.instructions.assert_.test_resources.file_contents.util.expectation_utils import \
    expectation_that_file_for_expected_contents_is_invalid
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import source_is_at_end, \
    is_at_beginning_of_line
from exactly_lib_test.tcfs.test_resources.sub_dir_of_sds_act import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.tcfs.test_resources.tcds_populators import \
    TcdsPopulator
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_utils.string_matcher.test_resources import contents_transformation
from exactly_lib_test.test_case_utils.string_matcher.test_resources.arguments_building import args
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt
from exactly_lib_test.test_resources.files.file_structure import DirContents, File, Dir
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    TcdsAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_transformer.test_resources import string_transformers
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes_str


class InstructionTestConfigurationForEquals(InstructionTestConfigurationForContentsOrEquals):
    def arrangement_for_actual_and_expected(self,
                                            actual_contents: str,
                                            expected: TcdsPopulator,
                                            post_sds_population_action: TcdsAction = TcdsAction(),
                                            symbols: SymbolTable = None,
                                            ) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()


def suite_for(instruction_configuration: InstructionTestConfigurationForEquals) -> unittest.TestSuite:
    test_cases_for_rel_opts = [
        _ErrorWhenExpectedFileDoesNotExist,
        _ErrorWhenExpectedFileIsADirectory,
        _ContentsDiffer,
        _ContentsEquals,

        _WhenStringTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents,
    ]

    test_cases_without_rel_opts = [
        _ContentsEqualsAHereDocument,
        _ContentsEqualsAString,
        _ContentsEqualsAStringAndFollowingLine,
        _ContentsEqualsAHereDocumentWithSymbolReferences,
        _ContentsDoNotEqualAHereDocument,
    ]

    return unittest.TestSuite([
        suite_for__conf__rel_opts__negations(instruction_configuration,
                                             _RELATIVITY_OPTION_CONFIGURATIONS_FOR_EXPECTED_FILE,
                                             test_cases_for_rel_opts),
        suite_for__conf__not_argument(instruction_configuration,
                                      test_cases_without_rel_opts),
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


class _ErrorWhenExpectedFileDoesNotExist(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check_with_source_variants(
            self.configuration.arguments_for(
                args('{maybe_not} {equals} {file_option} {relativity_option} non-existing-file.txt',
                     maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                     relativity_option=self.rel_opt.option_argument)),
            ArrangementPostAct(
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            expectation_that_file_for_expected_contents_is_invalid(self.rel_opt),
        )


class _ErrorWhenExpectedFileIsADirectory(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check_with_source_variants(
            self.configuration.arguments_for(
                args('{maybe_not} {equals} {file_option} {relativity_option} dir',
                     maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                     relativity_option=self.rel_opt.option_argument)),
            ArrangementPostAct(
                tcds_contents=self.rel_opt.populator_for_relativity_option_root(
                    DirContents([Dir.empty('dir')])),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            expectation_that_file_for_expected_contents_is_invalid(self.rel_opt),
        )


class _ContentsDiffer(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check_with_source_variants(
            self.configuration.arguments_for(
                args('{maybe_not} {equals} {file_option} {relativity_option} expected.txt',
                     maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                     relativity_option=self.rel_opt.option_argument)),
            self.configuration.arrangement_for_actual_and_expected(
                'actual',
                self.rel_opt.populator_for_relativity_option_root(
                    DirContents([File('expected.txt', 'expected')])),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            Expectation(
                main_result=self.not_opt.fail__if_positive__pass_if_negative,
                symbol_usages=self.rel_opt.symbols.usages_expectation(),
            ),
        )


class _ContentsEquals(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check_with_source_variants(
            self.configuration.arguments_for(
                args('{maybe_not} {equals} {file_option} {relativity_option} expected.txt',
                     maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                     relativity_option=self.rel_opt.option_argument)),
            self.configuration.arrangement_for_actual_and_expected(
                'expected',
                self.rel_opt.populator_for_relativity_option_root(
                    DirContents([File('expected.txt', 'expected')])),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            Expectation(
                main_result=self.not_opt.pass__if_positive__fail__if_negative,
                symbol_usages=self.rel_opt.symbols.usages_expectation(),
            ),
        )


class _ContentsEqualsAHereDocument(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{maybe_not} {equals} <<EOF',
                     maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative),
                ['expected content line',
                 'EOF']),
            self.configuration.arrangement_for_contents(
                lines_content(['expected content line']),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY),
            Expectation(main_result=self.maybe_not.pass__if_positive__fail__if_negative,
                        source=source_is_at_end),
        )


class _ContentsEqualsAString(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        expected_contents = 'expected contents'
        self._check(
            self.configuration.source_for(
                args('{maybe_not} {equals} {expected_contents}',
                     expected_contents=surrounded_by_hard_quotes_str(expected_contents),
                     maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative),
            ),
            self.configuration.arrangement_for_contents(
                expected_contents,
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY),
            Expectation(main_result=self.maybe_not.pass__if_positive__fail__if_negative,
                        source=source_is_at_end),
        )


class _ContentsEqualsAStringAndFollowingLine(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        expected_contents = 'expected contents'
        self._check(
            self.configuration.source_for(
                args('{maybe_not} {equals} {expected_contents}  ',
                     expected_contents=surrounded_by_hard_quotes_str(expected_contents),
                     maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative),
                ['following line']
            ),
            self.configuration.arrangement_for_contents(
                expected_contents,
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY),
            Expectation(main_result=self.maybe_not.pass__if_positive__fail__if_negative,
                        source=asrt_source.is_at_beginning_of_line(2)),
        )


class _ContentsEqualsAHereDocumentWithSymbolReferences(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        expected_content_line_template = 'expected content line, with {symbol} ref'

        def expected_content(symbol_content: str) -> str:
            return expected_content_line_template.format(symbol=symbol_content)

        symbol = StringConstantSymbolContext('symbol_name', 'the symbol value')
        self._check(
            self.configuration.source_for(
                args('{maybe_not} {equals} <<EOF',
                     maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative),
                [expected_content(symbol.name__sym_ref_syntax),
                 'EOF',
                 'following line']),
            self.configuration.arrangement_for_contents(
                lines_content([expected_content(symbol.str_value)]),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=symbol.symbol_table),
            Expectation(main_result=self.maybe_not.pass__if_positive__fail__if_negative,
                        symbol_usages=asrt.matches_sequence([
                            symbol.reference_assertion__any_data_type
                        ]),
                        source=is_at_beginning_of_line(4)),
        )


class _ContentsDoNotEqualAHereDocument(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{maybe_not} {equals} <<EOF',
                     maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative),
                ['expected content line',
                 'EOF',
                 'the following line']),
            self.configuration.arrangement_for_contents(
                lines_content(['actual contents that is not equal to expected contents']),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY),
            Expectation(main_result=self.maybe_not.fail__if_positive__pass_if_negative,
                        source=is_at_beginning_of_line(4)),
        )


class _WhenStringTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents(
    TestWithConfigurationAndRelativityOptionAndNegationBase):
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

        expected_symbol_usages = asrt.matches_sequence(
            [named_transformer.reference_assertion] +
            self.rel_opt.symbols.usage_expectation_assertions()
        )
        self._check_with_source_variants(
            self.configuration.arguments_for(
                args(
                    '{transform_option} {transformer} {maybe_not} {equals} '
                    '{file_option} {relativity_option} expected.txt',
                    transformer=named_transformer.name,
                    maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                    relativity_option=self.rel_opt.option_argument)),
            self.configuration.arrangement_for_contents(
                contents_generator.original,
                tcds_contents=self.rel_opt.populator_for_relativity_option_root(DirContents([
                    File('expected.txt', contents_generator.transformed)
                ])),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=symbols,
            ),
            Expectation(
                main_result=self.not_opt.pass__if_positive__fail__if_negative,
                symbol_usages=expected_symbol_usages,
            ),
        )
