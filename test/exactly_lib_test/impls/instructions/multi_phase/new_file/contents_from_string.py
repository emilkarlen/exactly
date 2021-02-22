import unittest
from typing import Callable

from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import QuoteType
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources import abstract_syntax as instr_abs_stx
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources import common_test_cases
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources import integration_check
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.abstract_syntax import \
    ExplicitContentsVariantAbsStx
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.defs import DISALLOWED_DST_RELATIVITIES, \
    ARBITRARY_ALLOWED_DST_FILE_RELATIVITY, ALLOWED_DST_FILE_RELATIVITIES, ACCEPTED_DST_RELATIVITY_VARIANTS
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.parse_check import \
    check_invalid_syntax__abs_stx
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.utils import \
    IS_SUCCESS
from exactly_lib_test.impls.instructions.multi_phase.test_resources.embryo_arr_exp import Arrangement, \
    MultiSourceExpectation, Expectation
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntaxes as string_source_abs_stx
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntaxes import StringSourceOfStringAbsStx
from exactly_lib_test.impls.types.test_resources.relativity_options import conf_rel_any
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources.sds_check.sds_contents_check import \
    non_hds_dir_contains_exactly, dir_contains_exactly
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.source import custom_abstract_syntax as custom_abs_stx
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR
from exactly_lib_test.test_resources.value_assertions import file_assertions as f_asrt, value_assertion as asrt
from exactly_lib_test.type_val_deps.test_resources.data import data_restrictions_assertions as asrt_rest
from exactly_lib_test.type_val_deps.types.path.test_resources import abstract_syntaxes as path_abs_stx
from exactly_lib_test.type_val_deps.types.path.test_resources.path import ConstantSuffixPathDdvSymbolContext
from exactly_lib_test.type_val_deps.types.string.test_resources import abstract_syntaxes as str_abs_stx
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntax import StringAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulScenariosWithConstantContents),
        unittest.makeSuite(TestFailingParse),
        unittest.makeSuite(TestSymbolReferences),
        unittest.makeSuite(TestCommonFailingScenariosDueToInvalidDestinationFile),
    ])


class TestSuccessfulScenariosWithConstantContents(unittest.TestCase):
    def test_contents_from_string__w_dst_relativity_variants(self):
        # ARRANGE #
        string_value = str_abs_stx.StringLiteralAbsStx('the_string_value')
        expected_file = fs.File('a-file-name.txt', string_value.value)
        for phase_is_after_act in [False, True]:
            checker = integration_check.checker(phase_is_after_act)
            for rel_opt_conf in ALLOWED_DST_FILE_RELATIVITIES:
                dst_path = rel_opt_conf.path_abs_stx_of_name(expected_file.name)
                instruction_syntax = instr_abs_stx.with_explicit_contents(
                    dst_path,
                    string_source_abs_stx.StringSourceOfStringAbsStx(string_value),
                )
                with self.subTest(relativity_option_string=rel_opt_conf.option_string,
                                  phase_is_after_act=phase_is_after_act):
                    # ACT & ASSERT #
                    checker.check__abs_stx__std_layouts_and_source_variants(
                        self,
                        instruction_syntax,
                        Arrangement.phase_agnostic(
                            pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                        ),
                        MultiSourceExpectation.phase_agnostic(
                            main_result=IS_SUCCESS,
                            side_effects_on_hds=f_asrt.dir_is_empty(),
                            symbol_usages=asrt.is_empty_sequence,
                            main_side_effects_on_sds=non_hds_dir_contains_exactly(rel_opt_conf.root_dir__non_hds,
                                                                                  fs.DirContents([expected_file])),
                        )
                    )

    def test_contents_from_here_doc(self):
        # ARRANGE #
        string_value = str_abs_stx.StringHereDocAbsStx('single line in here doc\n')
        expected_file = fs.File('a-file-name.txt', string_value.value)
        rel_opt_conf = ARBITRARY_ALLOWED_DST_FILE_RELATIVITY
        dst_path = rel_opt_conf.path_abs_stx_of_name(expected_file.name)
        instruction_syntax = instr_abs_stx.with_explicit_contents(
            dst_path,
            string_source_abs_stx.StringSourceOfStringAbsStx(string_value),
        )
        for phase_is_after_act in [False, True]:
            checker = integration_check.checker(phase_is_after_act)
            with self.subTest(phase_is_after_act=phase_is_after_act):
                # ACT & ASSERT #
                checker.check__abs_stx__std_layouts_and_source_variants(
                    self,
                    instruction_syntax,
                    Arrangement.phase_agnostic(
                        pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                    ),
                    MultiSourceExpectation.phase_agnostic(
                        main_result=IS_SUCCESS,
                        side_effects_on_hds=f_asrt.dir_is_empty(),
                        symbol_usages=asrt.is_empty_sequence,
                        main_side_effects_on_sds=non_hds_dir_contains_exactly(
                            rel_opt_conf.root_dir__non_hds,
                            fs.DirContents([expected_file])
                        ),
                    )
                )


class TestSymbolReferences(unittest.TestCase):
    def test_symbol_reference_in_dst_file_argument(self):
        dst_path_symbol = ConstantSuffixPathDdvSymbolContext('dst_path_symbol',
                                                             RelOptionType.REL_ACT,
                                                             'dst-file.txt',
                                                             ACCEPTED_DST_RELATIVITY_VARIANTS)
        string_value = str_abs_stx.StringHereDocAbsStx('single line in here doc\n')
        instruction_syntax = instr_abs_stx.with_explicit_contents(
            dst_path_symbol.abstract_syntax,
            string_source_abs_stx.StringSourceOfStringAbsStx(string_value),
        )

        expected_file = fs.File(dst_path_symbol.path_suffix, string_value.value)
        integration_check.CHECKER__BEFORE_ACT.check__abs_stx(
            self,
            instruction_syntax,
            Arrangement.phase_agnostic(
                pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                symbols=dst_path_symbol.symbol_table,
            ),
            Expectation.phase_agnostic(
                main_result=IS_SUCCESS,
                symbol_usages=asrt.matches_singleton_sequence(dst_path_symbol.reference_assertion),
                main_side_effects_on_sds=dir_contains_exactly(
                    dst_path_symbol.rel_option_type,
                    fs.DirContents([expected_file])
                ),
            )
        )

    def test_symbol_reference_in_file_argument_and_string(self):
        string_value_template = 'pre symbol {symbol} post symbol'

        def symbol_value_2_expected_contents(symbol_value: str) -> str:
            return string_value_template.format(symbol=symbol_value)

        def symbol_ref_syntax_2_contents_arguments(syntax: str) -> StringAbsStx:
            string_value = string_value_template.format(symbol=syntax)
            return str_abs_stx.StringLiteralAbsStx(string_value, QuoteType.SOFT)

        self._test_symbol_reference_in_dst_file_and_contents(symbol_ref_syntax_2_contents_arguments,
                                                             symbol_value_2_expected_contents)

    def test_symbol_reference_in_file_argument_and_here_document(self):
        here_doc_line_template = 'pre symbol {symbol} post symbol'

        def symbol_value_2_expected_contents(symbol_value: str) -> str:
            return here_doc_line_template.format(symbol=symbol_value) + '\n'

        def symbol_ref_syntax_2_contents_arguments(syntax: str) -> StringAbsStx:
            return str_abs_stx.StringHereDocAbsStx.of_lines__wo_new_lines([
                here_doc_line_template.format(symbol=syntax)
            ])

        self._test_symbol_reference_in_dst_file_and_contents(symbol_ref_syntax_2_contents_arguments,
                                                             symbol_value_2_expected_contents)

    def _test_symbol_reference_in_dst_file_and_contents(
            self,
            symbol_ref_syntax_2_contents_arguments: Callable[[str], StringAbsStx],
            symbol_value_2_expected_contents: Callable[[str], str]
    ):
        sub_dir_symbol = ConstantSuffixPathDdvSymbolContext(
            'sub_dir_symbol',
            RelOptionType.REL_ACT,
            'sub-dir',
            ACCEPTED_DST_RELATIVITY_VARIANTS,
        )
        contents_symbol = StringConstantSymbolContext(
            'contents_symbol_name',
            'contents symbol value',
            default_restrictions=asrt_rest.is_reference_restrictions__convertible_to_string(),
        )

        expected_file_contents = symbol_value_2_expected_contents(contents_symbol.str_value)

        expected_file = fs.File('a-file-name.txt', expected_file_contents)

        symbols = [sub_dir_symbol, contents_symbol]
        expected_symbol_references = SymbolContext.references_assertion_of_contexts(symbols)
        symbol_table = SymbolContext.symbol_table_of_contexts(symbols)

        contents_arguments = symbol_ref_syntax_2_contents_arguments(
            symbol_reference_syntax_for_name(contents_symbol.name))

        instruction_syntax = instr_abs_stx.with_explicit_contents(
            path_abs_stx.PathStringAbsStx.of_plain_components(
                [sub_dir_symbol.name__sym_ref_syntax, expected_file.name]
            ),
            StringSourceOfStringAbsStx(contents_arguments),
        )

        integration_check.CHECKER__AFTER_ACT.check__abs_stx(
            self,
            instruction_syntax,
            Arrangement.phase_agnostic(
                pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                symbols=symbol_table,
            ),
            Expectation.phase_agnostic(
                main_result=IS_SUCCESS,
                symbol_usages=expected_symbol_references,
                main_side_effects_on_sds=dir_contains_exactly(
                    sub_dir_symbol.rel_option_type,
                    fs.DirContents([
                        fs.Dir(sub_dir_symbol.path_suffix, [expected_file])])),
            ))


class TestFailingParse(unittest.TestCase):
    def test_disallowed_relativities(self):
        # ARRANGE #
        arguments_cases = [
            NameAndValue(
                'here doc',
                string_source_abs_stx.StringSourceOfStringAbsStx(
                    str_abs_stx.StringHereDocAbsStx('contents line\n'))
            ),
            NameAndValue(
                'raw string',
                string_source_abs_stx.StringSourceOfStringAbsStx(
                    str_abs_stx.StringLiteralAbsStx('raw_string_argument'))
            ),
            NameAndValue(
                'quoted string',
                string_source_abs_stx.StringSourceOfStringAbsStx(
                    str_abs_stx.StringLiteralAbsStx('quoted string argument', QuoteType.SOFT))
            ),
        ]
        for relativity in DISALLOWED_DST_RELATIVITIES:
            relativity_conf = conf_rel_any(relativity)
            for contents_case in arguments_cases:
                instruction_syntax = instr_abs_stx.with_explicit_contents(
                    relativity_conf.path_abs_stx_of_name('file-name'),
                    contents_case.value,
                )
                with self.subTest(relativity=str(relativity),
                                  contents=contents_case.name):
                    # ACT & ASSERT #
                    check_invalid_syntax__abs_stx(self, instruction_syntax)

    def test_fail_when_contents_is_missing(self):
        # ARRANGE #
        missing_contents = instr_abs_stx.CustomExplicitContentsVariantAbsStx(TokenSequence.empty())
        instruction_syntax = instr_abs_stx.InstructionAbsStx(
            path_abs_stx.DefaultRelPathAbsStx('file-name'),
            missing_contents,
        )
        # ACT & ASSERT #
        check_invalid_syntax__abs_stx(self, instruction_syntax)

    def test_fail_when_superfluous_arguments(self):
        # ARRANGE #
        valid_instruction_syntax = instr_abs_stx.with_explicit_contents(
            path_abs_stx.DefaultRelPathAbsStx('file-name'),
            string_source_abs_stx.StringSourceOfStringAbsStx(str_abs_stx.StringLiteralAbsStx('string')),
        )
        invalid_instruction_syntax = custom_abs_stx.SequenceAbsStx([
            valid_instruction_syntax,
            custom_abs_stx.CustomAbstractSyntax.singleton('superfluous_argument')
        ])
        # ACT & ASSERT #
        check_invalid_syntax__abs_stx(self, invalid_instruction_syntax)


class TestCommonFailingScenariosDueToInvalidDestinationFile(
    common_test_cases.TestCommonFailingScenariosDueToInvalidDestinationFileBase):
    def _file_contents_cases(self) -> common_test_cases.InvalidDestinationFileTestCasesData:
        file_contents_cases = [
            NameAndValue(
                'contents of here doc',
                ExplicitContentsVariantAbsStx(
                    string_source_abs_stx.StringSourceOfStringAbsStx(
                        str_abs_stx.StringHereDocAbsStx('contents\n')
                    )
                )
            ),
            NameAndValue(
                'contents of string',
                ExplicitContentsVariantAbsStx(
                    string_source_abs_stx.StringSourceOfStringAbsStx(
                        str_abs_stx.StringLiteralAbsStx('contents')
                    )
                )
            ),
        ]

        return common_test_cases.InvalidDestinationFileTestCasesData(
            file_contents_cases,
            empty_symbol_table())
