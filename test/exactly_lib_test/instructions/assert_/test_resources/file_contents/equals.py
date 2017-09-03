import unittest

from exactly_lib.instructions.assert_.utils.file_contents.parsing import EXPECTED_FILE_REL_OPT_ARG_CONFIG
from exactly_lib.named_element.named_element_usage import NamedElementReference
from exactly_lib.named_element.symbol.restrictions.reference_restrictions import is_any_data_type
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.lines_transformers.resolvers import LinesTransformerConstant
from exactly_lib.test_case_utils.parse.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.string import lines_content
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents import contents_transformation
from exactly_lib_test.instructions.assert_.test_resources.file_contents.arrangement_utils import \
    populator_for_relativity_option_root_for_contents_from_fun
from exactly_lib_test.instructions.assert_.test_resources.file_contents.expectation_utils import \
    expectation_that_file_for_expected_contents_is_invalid
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    args, InstructionTestConfigurationForContentsOrEquals, TestWithConfigurationAndNegationArgumentBase, \
    suite_for__conf__not_argument
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    suite_for__conf__rel_opts__negations, RelativityOptionConfigurationForRelCwdForTestCwdDir, \
    TestWithConfigurationAndRelativityOptionAndNegationBase, MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources import relativity_options as rel_opt
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.named_element.symbol.test_resources import symbol_utils
from exactly_lib_test.named_element.symbol.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.named_element.test_resources.lines_transformer import is_lines_transformer_reference_to
from exactly_lib_test.named_element.test_resources.named_elem_utils import container
from exactly_lib_test.section_document.test_resources.parse_source_assertions import source_is_at_end, \
    is_at_beginning_of_line
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_and_sds_populators import \
    HomeOrSdsPopulator
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, File
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class InstructionTestConfigurationForEquals(InstructionTestConfigurationForContentsOrEquals):
    def arrangement_for_actual_and_expected(self,
                                            actual_contents: str,
                                            expected: HomeOrSdsPopulator,
                                            post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                            symbols: SymbolTable = None,
                                            ) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()


def suite_for(instruction_configuration: InstructionTestConfigurationForEquals) -> unittest.TestSuite:
    test_cases_for_rel_opts = [
        _ErrorWhenExpectedFileDoesNotExist,
        _ErrorWhenExpectedFileIsADirectory,
        _ContentsDiffer,
        _ContentsEquals,

        _WhenLinesTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents,
    ]

    test_cases_without_rel_opts = [
        _ContentsEqualsAHereDocument,
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
    rel_opt.conf_rel_any(RelOptionType.REL_HOME_CASE),
    RelativityOptionConfigurationForRelCwdForTestCwdDir(),
    rel_opt.conf_rel_any(RelOptionType.REL_ACT),
    rel_opt.conf_rel_any(RelOptionType.REL_TMP),
    rel_opt.default_conf_rel_any(RelOptionType.REL_HOME_CASE),
    rel_opt.symbol_conf_rel_any(RelOptionType.REL_TMP,
                                'EXPECTED_FILE_SYMBOL',
                                EXPECTED_FILE_REL_OPT_ARG_CONFIG.options.accepted_relativity_variants),
    rel_opt.symbol_conf_rel_any(RelOptionType.REL_HOME_CASE,
                                'EXPECTED_FILE_SYMBOL',
                                EXPECTED_FILE_REL_OPT_ARG_CONFIG.options.accepted_relativity_variants),
]

_TRANSFORMER_SYMBOL_NAME = 'the_transformer'


class _ErrorWhenExpectedFileDoesNotExist(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            self.configuration.first_line_argument(
                args('{maybe_not} {equals} {relativity_option} non-existing-file.txt',
                     maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                     relativity_option=self.rel_opt.option_string)),
            ArrangementPostAct(
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            expectation_that_file_for_expected_contents_is_invalid(self.rel_opt),
        )


class _ErrorWhenExpectedFileIsADirectory(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            self.configuration.first_line_argument(
                args('{maybe_not} {equals} {relativity_option} dir',
                     maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                     relativity_option=self.rel_opt.option_string)),
            ArrangementPostAct(
                home_or_sds_contents=self.rel_opt.populator_for_relativity_option_root(
                    DirContents([empty_dir('dir')])),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            expectation_that_file_for_expected_contents_is_invalid(self.rel_opt),
        )


class _ContentsDiffer(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            self.configuration.first_line_argument(
                args('{maybe_not} {equals} {relativity_option} expected.txt',
                     maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                     relativity_option=self.rel_opt.option_string)),
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
        self._check_single_instruction_line_with_source_variants(
            self.configuration.first_line_argument(
                args('{maybe_not} {equals} {relativity_option} expected.txt',
                     maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                     relativity_option=self.rel_opt.option_string)),
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


class _ContentsEqualsAHereDocumentWithSymbolReferences(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        expected_content_line_template = 'expected content line, with {symbol} ref'

        def expected_content(symbol_content: str) -> str:
            return expected_content_line_template.format(symbol=symbol_content)

        symbol = NameAndValue('symbol_name', 'the symbol value')
        self._check(
            self.configuration.source_for(
                args('{maybe_not} {equals} <<EOF',
                     maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative),
                [expected_content(symbol_reference_syntax_for_name(symbol.name)),
                 'EOF',
                 'following line']),
            self.configuration.arrangement_for_contents(
                lines_content([expected_content(symbol.value)]),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=SymbolTable({
                    symbol.name: symbol_utils.string_constant_container(symbol.value),
                })),
            Expectation(main_result=self.maybe_not.pass__if_positive__fail__if_negative,
                        symbol_usages=equals_symbol_references([
                            NamedElementReference(symbol.name, is_any_data_type())
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


class _WhenLinesTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents(
    TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        # ARRANGE #
        named_transformer = NameAndValue(_TRANSFORMER_SYMBOL_NAME,
                                         LinesTransformerConstant(
                                             contents_transformation.ToUppercaseLinesTransformer()))

        contents_generator = contents_transformation.TransformedContentsSetup(
            original='some\ntext',
            transformed='SOME\nTEXT',
        )

        symbols = self.rel_opt.symbols.in_arrangement()
        symbols.put(named_transformer.name,
                    container(named_transformer.value))

        expected_symbol_reference_to_transformer = is_lines_transformer_reference_to(named_transformer.name)

        expected_symbol_usages = asrt.matches_sequence(
            [expected_symbol_reference_to_transformer] +
            self.rel_opt.symbols.usage_expectation_assertions()
        )
        self._check_single_instruction_line_with_source_variants(
            self.configuration.first_line_argument(
                args('{transform_option} {transformer} {maybe_not} {equals} {relativity_option} expected.txt',
                     transformer=named_transformer.name,
                     maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                     relativity_option=self.rel_opt.option_string)),
            self.configuration.arrangement_for_contents_from_fun(
                contents_generator.contents_before_replacement,
                home_or_sds_contents=populator_for_relativity_option_root_for_contents_from_fun(
                    self.rel_opt,
                    'expected.txt',
                    contents_generator.expected_contents_after_replacement
                ),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=symbols,
            ),
            Expectation(
                main_result=self.not_opt.pass__if_positive__fail__if_negative,
                symbol_usages=expected_symbol_usages,
            ),
        )
