import unittest
from typing import Sequence, Callable

from exactly_lib.impls.instructions.multi_phase.new_file import parse as sut, defs
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.path_relativity import RelHdsOptionType, RelOptionType, RelSdsOptionType, RelNonHdsOptionType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources import abstract_syntax as instr_abs_stx
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources import common_test_cases
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources import integration_check
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.abstract_syntax import \
    ExplicitContentsVariantAbsStx
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.common_test_cases import \
    InvalidDestinationFileTestCasesData
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.defs import \
    ALLOWED_SRC_FILE_RELATIVITIES__BEFORE_ACT, accepted_src_file_relativities, accepted_non_hds_source_relativities, \
    ALLOWED_DST_FILE_RELATIVITIES
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.parse_check import \
    check_invalid_syntax__abs_stx
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.utils import Step, \
    IS_FAILURE, IS_SUCCESS
from exactly_lib_test.impls.instructions.multi_phase.test_resources.instruction_embryo_check import \
    MultiSourceExpectation
from exactly_lib_test.impls.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntaxes as string_source_abs_stx
from exactly_lib_test.impls.types.string_transformer.test_resources import abstract_syntaxes as str_trans_abs_stx
from exactly_lib_test.impls.types.test_resources.relativity_options import conf_rel_hds, every_conf_rel_hds, \
    conf_rel_non_hds, conf_rel_any, RelativityOptionConfigurationForRelNonHds, RelativityOptionConfiguration, \
    conf_rel_sds
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import DirContents, sym_link, File, Dir
from exactly_lib_test.test_resources.source import custom_abstract_syntax as custom_abs_stx
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_deps.types.path.test_resources import abstract_syntaxes as path_abs_stx
from exactly_lib_test.type_val_deps.types.path.test_resources.path import ConstantSuffixPathDdvSymbolContext
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.abstract_syntax import \
    StringTransformerSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.assertions import \
    is_reference_to_string_transformer__usage
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.type_val_prims.string_transformer.test_resources import string_transformers


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestScenariosWithContentsFromFile),
        unittest.makeSuite(TestCommonFailingScenariosDueToInvalidDestinationFile),
    ])


class TestScenariosWithContentsFromFile(unittest.TestCase):
    src_file_name = 'src-file.txt'

    src_file_variants = [
        NameAndValue('no file',
                     DirContents([])),
        NameAndValue('file is a directory',
                     DirContents([Dir.empty(src_file_name)])),
        NameAndValue('file is a broken symlink',
                     DirContents([sym_link(src_file_name, 'non-existing-target-file')])),
    ]

    def test_symbol_usages(self):
        # ARRANGE #

        to_upper_transformer = StringTransformerSymbolContext.of_primitive(
            'TRANSFORMER_SYMBOL',
            string_transformers.to_uppercase(),
        )

        src_file = fs.File('src-file.txt', 'contents of source file')
        src_file_rel_conf = conf_rel_hds(RelHdsOptionType.REL_HDS_CASE)

        expected_dst_file = fs.File('dst-file-name.txt', src_file.contents.upper())

        dst_file_symbol = ConstantSuffixPathDdvSymbolContext(
            'DST_FILE_SYMBOL',
            RelOptionType.REL_TMP,
            expected_dst_file.name,
            sut.REL_OPT_ARG_CONF.options.accepted_relativity_variants,
        )

        for phase_is_after_act in [False, True]:
            checker = integration_check.checker(phase_is_after_act)
            src_file_rel_opt_conf = defs.src_rel_opt_arg_conf_for_phase(phase_is_after_act)

            src_file_symbol = ConstantSuffixPathDdvSymbolContext(
                'SRC_FILE_SYMBOL',
                src_file_rel_conf.relativity_option,
                src_file.name,
                src_file_rel_opt_conf.accepted_relativity_variants,
            )
            transformed_file_contents = string_source_abs_stx.TransformedStringSourceAbsStx(
                string_source_abs_stx.StringSourceOfFileAbsStx(src_file_symbol.abs_stx_of_reference),
                StringTransformerSymbolReferenceAbsStx(to_upper_transformer.name)
            )
            instruction_syntax = instr_abs_stx.with_explicit_contents(
                dst_file_symbol.abs_stx_of_reference,
                transformed_file_contents,
            )
            symbols = SymbolContext.symbol_table_of_contexts([
                dst_file_symbol,
                src_file_symbol,
                to_upper_transformer,
            ])

            with self.subTest(phase_is_after_act=phase_is_after_act):
                # ACT & ASSERT #
                checker.check__abs_stx__std_layouts_and_source_variants(
                    self,
                    instruction_syntax,
                    ArrangementWithSds(
                        symbols=symbols,
                        hds_contents=src_file_rel_conf.populator_for_relativity_option_root__hds(
                            DirContents([src_file]))
                    ),
                    MultiSourceExpectation(
                        main_result=IS_SUCCESS,
                        symbol_usages=asrt.matches_sequence([
                            dst_file_symbol.reference_assertion__path_or_string,
                            src_file_symbol.reference_assertion__path_or_string,
                            is_reference_to_string_transformer__usage(to_upper_transformer.name),
                        ]),
                    ),
                )

    def test_superfluous_arguments(self):
        # ARRANGE #
        arbitrary_transformer_symbol = StringTransformerSymbolContext.of_arbitrary_value('TRANSFORMER_SYMBOL')

        src_file_relativity_conf = conf_rel_hds(RelHdsOptionType.REL_HDS_CASE)

        file_contents_builder = string_source_abs_stx.TransformableAbsStxBuilder(
            string_source_abs_stx.StringSourceOfFileAbsStx(
                src_file_relativity_conf.path_abs_stx_of_name('src-file.txt')
            )
        )

        file_contents_cases = [
            NameAndValue(
                'contents of existing file / without transformation',
                file_contents_builder.without_transformation()
            ),
            NameAndValue(
                'contents of existing file / with transformation',
                file_contents_builder.with_transformation(arbitrary_transformer_symbol.abs_stx_of_reference)
            ),
        ]

        for file_contents_case in file_contents_cases:
            valid_instruction_syntax = instr_abs_stx.with_explicit_contents(
                path_abs_stx.DefaultRelPathAbsStx('dst-file.txt'),
                file_contents_case.value,
            )
            invalid_instruction_syntax = custom_abs_stx.SequenceAbstractSyntax([
                valid_instruction_syntax,
                custom_abs_stx.CustomAbstractSyntax.singleton('superfluous_argument')
            ])
            with self.subTest(file_contents_variant=file_contents_case.name):
                # ACT & ASSERT #
                check_invalid_syntax__abs_stx(self, invalid_instruction_syntax)

    def test_validation_pre_sds_SHOULD_fail_WHEN_source_is_not_an_existing_file_rel_hds(self):
        self._check_of_invalid_src_file(lambda x: every_conf_rel_hds(),
                                        Step.VALIDATE_PRE_SDS)

    def test_main_SHOULD_fail_WHEN_source_is_not_an_existing_file_rel_non_hds(self):
        def every_src_file_rel_conf(is_before_act: bool) -> Sequence[RelativityOptionConfiguration]:
            return [
                conf_rel_non_hds(relativity)
                for relativity in accepted_non_hds_source_relativities(is_before_act)
            ]

        self._check_of_invalid_src_file(every_src_file_rel_conf, Step.MAIN)

    def test_all_relativities__without_transformer(self):
        # ARRANGE #

        src_file = fs.File('source-file.txt', 'contents of source file')
        expected_file = fs.File('a-file-name.txt', src_file.contents)

        for phase_is_after_act in [False, True]:
            checker = integration_check.checker(phase_is_after_act)
            for dst_rel_opt_conf in ALLOWED_DST_FILE_RELATIVITIES:
                for src_rel_opt_conf in accepted_src_file_relativities(phase_is_after_act):
                    file_contents_abs_stx = string_source_abs_stx.StringSourceOfFileAbsStx(
                        src_rel_opt_conf.path_abs_stx_of_name(src_file.name)
                    )
                    instruction_syntax = instr_abs_stx.with_explicit_contents(
                        dst_rel_opt_conf.path_abs_stx_of_name(expected_file.file_name),
                        file_contents_abs_stx,
                    )
                    expected_non_hds_contents = self._expected_non_hds_contents(
                        dst_rel_opt_conf,
                        expected_file,
                        src_rel_opt_conf,
                        src_file)

                    with self.subTest(phase_is_after_act=phase_is_after_act,
                                      dst_relativity=dst_rel_opt_conf.option_argument,
                                      src_relativity=src_rel_opt_conf.option_argument):
                        # ACT & ASSERT #
                        checker.check__abs_stx__std_layouts_and_source_variants(
                            self,
                            instruction_syntax,
                            ArrangementWithSds(
                                pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                                tcds_contents=src_rel_opt_conf.populator_for_relativity_option_root(
                                    DirContents([src_file]))
                            ),
                            MultiSourceExpectation(
                                main_result=IS_SUCCESS,
                                symbol_usages=asrt.is_empty_sequence,
                                main_side_effects_on_sds=expected_non_hds_contents,
                            )
                        )

    def test__with_transformer(self):
        # ARRANGE #
        src_file = fs.File('source-file.txt', 'contents of source file')
        expected_file = fs.File('a-file-name.txt', src_file.contents.upper())

        to_upper_transformer = StringTransformerSymbolContext.of_primitive(
            'TRANSFORMER_SYMBOL',
            string_transformers.to_uppercase(),
        )

        src_rel_opt_conf = ALLOWED_SRC_FILE_RELATIVITIES__BEFORE_ACT[0]
        dst_rel_opt_conf = conf_rel_non_hds(RelNonHdsOptionType.REL_ACT)

        expected_non_hds_contents = self._expected_non_hds_contents(
            dst_rel_opt_conf,
            expected_file,
            src_rel_opt_conf,
            src_file,
        )

        transformed_file_contents_abs_stx = string_source_abs_stx.TransformedStringSourceAbsStx(
            string_source_abs_stx.StringSourceOfFileAbsStx(
                src_rel_opt_conf.path_abs_stx_of_name(src_file.name)
            ),
            to_upper_transformer.abs_stx_of_reference,
        )
        instruction_syntax = instr_abs_stx.with_explicit_contents(
            dst_rel_opt_conf.path_abs_stx_of_name(expected_file.file_name),
            transformed_file_contents_abs_stx,
        )

        symbols = to_upper_transformer.symbol_table

        for phase_is_after_act in [False, True]:
            checker = integration_check.checker(phase_is_after_act)
            with self.subTest(phase_is_after_act=phase_is_after_act):
                # ACT & ASSERT #
                checker.check__abs_stx__std_layouts_and_source_variants(
                    self,
                    instruction_syntax,
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                        tcds_contents=src_rel_opt_conf.populator_for_relativity_option_root(
                            DirContents([src_file])),
                        symbols=symbols,
                    ),
                    MultiSourceExpectation(
                        main_result=IS_SUCCESS,
                        main_side_effects_on_sds=expected_non_hds_contents,
                        symbol_usages=to_upper_transformer.usages_assertion,
                    )
                )

    def test_string_transformer_should_be_parsed_as_simple_expression(self):
        # ARRANGE #
        transformation_w_infix_op = str_trans_abs_stx.StringTransformerCompositionAbsStx(
            [
                StringTransformerSymbolReferenceAbsStx('str_trans_1'),
                StringTransformerSymbolReferenceAbsStx('str_trans_2'),
            ],
            within_parens=False,
            allow_elements_on_separate_lines=False,
        )
        src_rel_opt_conf = conf_rel_sds(RelSdsOptionType.REL_ACT)
        file_contents_arg = string_source_abs_stx.TransformedStringSourceAbsStx(
            string_source_abs_stx.StringSourceOfFileAbsStx(
                src_rel_opt_conf.path_abs_stx_of_name('src-file')
            ),
            transformation_w_infix_op
        )
        instruction_syntax = instr_abs_stx.with_explicit_contents(
            path_abs_stx.DefaultRelPathAbsStx('dst-file'),
            file_contents_arg,
        )
        # ACT & ASSERT #
        check_invalid_syntax__abs_stx(self, instruction_syntax)

    @staticmethod
    def _expect_failure_in(step_of_expected_failure: Step) -> MultiSourceExpectation:
        symbol_usages_expectation = asrt.is_sequence_of(asrt.is_instance(SymbolReference))

        if step_of_expected_failure is Step.VALIDATE_PRE_SDS:
            return MultiSourceExpectation(validation=ValidationAssertions.pre_sds_fails__w_any_msg(),
                                          symbol_usages=symbol_usages_expectation)
        else:
            return MultiSourceExpectation(main_result=IS_FAILURE,
                                          symbol_usages=symbol_usages_expectation)

    def _check_of_invalid_src_file(
            self,
            is_after_act_2_every_src_file_rel_conf: Callable[[bool], Sequence[RelativityOptionConfiguration]],
            step_of_expected_failure: Step):
        # ARRANGE #
        transformer = StringTransformerSymbolContext.of_primitive(
            'TRANSFORMER_SYMBOL',
            string_transformers.to_uppercase(),
        )
        symbols = transformer.symbol_table

        dst_file_rel_conf = conf_rel_any(RelOptionType.REL_TMP)

        expectation_ = self._expect_failure_in(step_of_expected_failure)

        for phase_is_after_act in [False, True]:
            checker = integration_check.checker(phase_is_after_act)
            for src_file_rel_conf in is_after_act_2_every_src_file_rel_conf(phase_is_after_act):
                contents_builder = string_source_abs_stx.TransformableAbsStxBuilder(
                    string_source_abs_stx.StringSourceOfFileAbsStx(
                        src_file_rel_conf.path_abs_stx_of_name(self.src_file_name)
                    )
                )
                for actual_src_file_variant in self.src_file_variants:
                    for contents_arguments in contents_builder.with_and_without_transformer_cases(
                            transformer.abs_stx_of_reference):
                        instruction_syntax = instr_abs_stx.with_explicit_contents(
                            dst_file_rel_conf.path_abs_stx_of_name('dst-file.txt'),
                            contents_arguments.value,
                        )
                        with self.subTest(phase_is_after_act=phase_is_after_act,
                                          contents=contents_arguments.name,
                                          relativity_of_src_path=src_file_rel_conf.option_argument):
                            # ACT & ASSERT #
                            checker.check__abs_stx__std_layouts_and_source_variants(
                                self,
                                instruction_syntax,
                                ArrangementWithSds(
                                    pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                                    tcds_contents=src_file_rel_conf.populator_for_relativity_option_root(
                                        actual_src_file_variant.value),
                                    symbols=symbols,
                                ),
                                expectation_,
                            )

    @staticmethod
    def _expected_non_hds_contents(dst_file_rel_opt_conf: RelativityOptionConfigurationForRelNonHds,
                                   dst_file: fs.File,
                                   src_file_rel_opt_conf: RelativityOptionConfiguration,
                                   src_file: fs.File
                                   ) -> ValueAssertion:
        if dst_file_rel_opt_conf.option_argument_str == src_file_rel_opt_conf.option_string or \
                (dst_file_rel_opt_conf.is_rel_cwd and src_file_rel_opt_conf.is_rel_cwd):
            return dst_file_rel_opt_conf.assert_root_dir_contains_exactly(fs.DirContents([dst_file,
                                                                                          src_file]))
        else:
            return dst_file_rel_opt_conf.assert_root_dir_contains_exactly(fs.DirContents([dst_file]))


class TestCommonFailingScenariosDueToInvalidDestinationFile(
    common_test_cases.TestCommonFailingScenariosDueToInvalidDestinationFileBase):
    def _file_contents_cases(self) -> InvalidDestinationFileTestCasesData:
        arbitrary_transformer = StringTransformerSymbolContext.of_primitive(
            'TRANSFORMER_SYMBOL',
            string_transformers.to_uppercase(),
        )

        symbols = arbitrary_transformer.symbol_table

        relativity_conf = conf_rel_hds(RelHdsOptionType.REL_HDS_CASE)

        src_file = relativity_conf.path_abs_stx_of_name('src-file.txt')

        contents_abs_stx_builder = string_source_abs_stx.TransformableAbsStxBuilder(
            string_source_abs_stx.StringSourceOfFileAbsStx(src_file)
        )

        src_file_in_hds_contents = relativity_conf.populator_for_relativity_option_root(
            DirContents([File.empty(src_file.name)])
        )

        file_contents_cases = [
            NameAndValue(
                'contents of existing file / without transformation',
                ExplicitContentsVariantAbsStx(
                    contents_abs_stx_builder.without_transformation()
                )
            ),
            NameAndValue(
                'contents of existing file / with transformation',
                ExplicitContentsVariantAbsStx(
                    contents_abs_stx_builder.with_transformation(arbitrary_transformer.abs_stx_of_reference)
                )
            ),
        ]

        return InvalidDestinationFileTestCasesData(
            file_contents_cases,
            symbols,
            src_file_in_hds_contents)
