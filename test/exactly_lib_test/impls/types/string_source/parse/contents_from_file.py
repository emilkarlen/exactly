import unittest

from exactly_lib.impls.types.path.rel_opts_configuration import RelOptionsConfiguration
from exactly_lib.tcfs.path_relativity import RelHdsOptionType, RelOptionType, PathRelativityVariants
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Expectation, ParseExpectation
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, MultiSourceExpectation, \
    ExecutionExpectation
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntaxes as string_source_abs_stx
from exactly_lib_test.impls.types.string_source.test_resources import integration_check, parse_check
from exactly_lib_test.impls.types.string_transformers.test_resources import \
    validation_cases as str_trans_validation_cases, abstract_syntaxes as str_trans_abs_stx
from exactly_lib_test.impls.types.test_resources.relativity_options import conf_rel_hds, conf_rel_any
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import DirContents, sym_link, Dir
from exactly_lib_test.test_resources.source.abstract_syntax_impls import OptionallyOnNewLine
from exactly_lib_test.test_resources.source.layout import LayoutSpec
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.path.test_resources.path import ConstantSuffixPathDdvSymbolContext
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.abstract_syntax import \
    StringTransformerSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source
from exactly_lib_test.type_val_prims.string_transformer.test_resources import string_transformers


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulExecution),
        TestSymbolReferences(),
        unittest.makeSuite(TestValidation),
        unittest.makeSuite(TestSyntax),
    ])


class TestSuccessfulExecution(unittest.TestCase):
    def test_without_transformer(self):
        # ARRANGE #
        src_file = fs.File('source-file.txt', 'contents of source file')
        src_rel_opt_conf = conf_rel_any(RelOptionType.REL_TMP)

        checker = integration_check.checker(parse_check.rel_opts_conf_of_single(src_rel_opt_conf.relativity))

        file_contents_abs_stx = string_source_abs_stx.StringSourceOfFileAbsStx(
            src_rel_opt_conf.path_abs_stx_of_name(src_file.name)
        )
        # ACT & ASSERT #
        checker.check__abs_stx__layouts__std_source_variants__wo_input(
            self,
            OptionallyOnNewLine(file_contents_abs_stx),
            arrangement_w_tcds(
                tcds_contents=src_rel_opt_conf.populator_for_relativity_option_root(
                    DirContents([src_file]))
            ),
            MultiSourceExpectation.of_prim__const(
                asrt_string_source.pre_post_freeze__matches_str__const(
                    src_file.contents,
                    may_depend_on_external_resources=True,
                ),
                symbol_references=asrt.is_empty_sequence,
            )
        )

    def test__with_transformer(self):
        # ARRANGE #
        src_file = fs.File('source-file.txt', 'contents of source file')
        expected_contents = src_file.contents.upper()

        to_upper_transformer = StringTransformerSymbolContext.of_primitive(
            'TRANSFORMER_SYMBOL',
            string_transformers.to_uppercase(),
        )

        src_rel_opt_conf = conf_rel_any(RelOptionType.REL_TMP)

        transformed_file_contents_abs_stx = string_source_abs_stx.TransformedStringSourceAbsStx(
            string_source_abs_stx.StringSourceOfFileAbsStx(
                src_rel_opt_conf.path_abs_stx_of_name(src_file.name)
            ),
            to_upper_transformer.abs_stx_of_reference,
        )

        symbols = to_upper_transformer.symbol_table

        checker = integration_check.checker(parse_check.rel_opts_conf_of_single(src_rel_opt_conf.relativity))
        # ACT & ASSERT #
        checker.check__abs_stx__layouts__std_source_variants__wo_input(
            self,
            OptionallyOnNewLine(transformed_file_contents_abs_stx),
            arrangement_w_tcds(
                tcds_contents=src_rel_opt_conf.populator_for_relativity_option_root(
                    DirContents([src_file])),
                symbols=symbols,
            ),
            MultiSourceExpectation.of_prim__const(
                asrt_string_source.pre_post_freeze__matches_str__const(
                    expected_contents,
                    may_depend_on_external_resources=True,
                ),
                symbol_references=to_upper_transformer.references_assertion,
            )
        )


class TestSymbolReferences(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        to_upper_transformer = StringTransformerSymbolContext.of_primitive(
            'TRANSFORMER_SYMBOL',
            string_transformers.to_uppercase(),
        )

        src_file = fs.File('src-file.txt', 'contents of source file')
        src_file_rel_conf = conf_rel_hds(RelHdsOptionType.REL_HDS_CASE)

        expected_contents = src_file.contents.upper()

        path_relativity_variants = PathRelativityVariants({src_file_rel_conf.relativity}, True)
        checker = integration_check.checker(RelOptionsConfiguration(path_relativity_variants,
                                                                    src_file_rel_conf.relativity))

        src_file_symbol = ConstantSuffixPathDdvSymbolContext(
            'SRC_FILE_SYMBOL',
            src_file_rel_conf.relativity,
            src_file.name,
            path_relativity_variants,
        )
        string_source_syntax = string_source_abs_stx.TransformedStringSourceAbsStx(
            string_source_abs_stx.StringSourceOfFileAbsStx(src_file_symbol.abs_stx_of_reference),
            to_upper_transformer.abs_stx_of_reference,
        )
        symbol_table = SymbolContext.symbol_table_of_contexts([
            src_file_symbol,
            to_upper_transformer,
        ])

        # ACT & ASSERT #
        checker.check__abs_stx__layouts__std_source_variants__wo_input(
            self,
            OptionallyOnNewLine(string_source_syntax),
            arrangement_w_tcds(
                symbols=symbol_table,
                hds_contents=src_file_rel_conf.populator_for_relativity_option_root__hds(
                    DirContents([src_file]))
            ),
            MultiSourceExpectation.of_prim__const(
                asrt_string_source.pre_post_freeze__matches_str__const(
                    expected_contents,
                    may_depend_on_external_resources=True,
                ),
                symbol_references=asrt.matches_sequence([
                    src_file_symbol.reference_assertion__path_or_string,
                    to_upper_transformer.reference_assertion,
                ]),
            ),
        )


class TestValidation(unittest.TestCase):
    src_file_name = 'src-file.txt'

    src_file_variants = [
        NameAndValue('no file',
                     DirContents([])),
        NameAndValue('file is a directory',
                     DirContents([Dir.empty(src_file_name)])),
        NameAndValue('file is a broken symlink',
                     DirContents([sym_link(src_file_name, 'non-existing-target-file')])),
    ]

    def test_validation_pre_sds_SHOULD_fail_WHEN_source_is_not_an_existing_file_rel_hds(self):
        self._check_of_invalid_src_file(RelOptionType.REL_HDS_CASE,
                                        ValidationAssertions.pre_sds_fails__w_any_msg())

    def test_main_SHOULD_fail_WHEN_source_is_not_an_existing_file_rel_non_hds(self):
        self._check_of_invalid_src_file(RelOptionType.REL_ACT,
                                        ValidationAssertions.post_sds_fails__w_any_msg())

    def test_transformer_SHOULD_be_validated(self):
        src_file_rel_conf = conf_rel_any(RelOptionType.REL_HDS_CASE)
        src_file = fs.File.empty('src-file.txt')

        checker = integration_check.checker(parse_check.rel_opts_conf_of_single(src_file_rel_conf.relativity))

        file_string_source_syntax = string_source_abs_stx.StringSourceOfFileAbsStx(
            src_file_rel_conf.path_abs_stx_of_name(self.src_file_name)
        )
        str_trans_syntax = StringTransformerSymbolReferenceAbsStx(
            'INVALID_STRING_TRANSFORMER'
        )
        transformed_string_source_syntax = string_source_abs_stx.TransformedStringSourceAbsStx(
            file_string_source_syntax,
            str_trans_syntax,
        )

        for validation_case in str_trans_validation_cases.failing_validation_cases(str_trans_syntax.symbol_name):
            with self.subTest(validation_case.name):
                v_case = validation_case.value
                checker.check__abs_stx__layouts__std_source_variants__wo_input(
                    self,
                    OptionallyOnNewLine(transformed_string_source_syntax),
                    arrangement_w_tcds(
                        tcds_contents=src_file_rel_conf.populator_for_relativity_option_root(
                            fs.DirContents([src_file])
                        ),
                        symbols=v_case.symbol_context.symbol_table,
                    ),
                    MultiSourceExpectation(
                        symbol_references=v_case.symbol_context.references_assertion,
                        execution=ExecutionExpectation(
                            validation=v_case.expectation
                        )
                    ),
                )

    def _check_of_invalid_src_file(
            self,
            src_file_relativity: RelOptionType,
            validation: ValidationAssertions,
    ):
        # ARRANGE #
        checker = integration_check.checker(parse_check.rel_opts_conf_of_single(src_file_relativity))

        expectation_ = MultiSourceExpectation(
            symbol_references=asrt.anything_goes(),
            execution=ExecutionExpectation(
                validation=validation
            )
        )

        src_file_rel_conf = conf_rel_any(src_file_relativity)

        transformer = StringTransformerSymbolContext.of_primitive(
            'TRANSFORMER_SYMBOL',
            string_transformers.to_uppercase(),
        )
        symbols = transformer.symbol_table

        contents_builder = string_source_abs_stx.TransformableAbsStxBuilder(
            string_source_abs_stx.StringSourceOfFileAbsStx(
                src_file_rel_conf.path_abs_stx_of_name(self.src_file_name)
            )
        )
        for actual_src_file_variant in self.src_file_variants:
            for contents_arguments in contents_builder.with_and_without_transformer_cases(
                    transformer.abs_stx_of_reference):
                with self.subTest(src_file_variant=actual_src_file_variant.name,
                                  contents=contents_arguments.name,
                                  relativity_of_src_path=src_file_rel_conf.option_argument):
                    # ACT & ASSERT #
                    checker.check__abs_stx__layouts__std_source_variants__wo_input(
                        self,
                        OptionallyOnNewLine(contents_arguments.value),
                        arrangement_w_tcds(
                            tcds_contents=src_file_rel_conf.populator_for_relativity_option_root(
                                actual_src_file_variant.value),
                            symbols=symbols,
                        ),
                        expectation_,
                    )


class TestSyntax(unittest.TestCase):
    def test_string_transformer_should_be_parsed_as_simple_expression(self):
        # ARRANGE #
        the_layout = LayoutSpec.of_default()

        src_rel_opt_conf = conf_rel_any(RelOptionType.REL_TMP)

        src_file = fs.File('source-file.txt', 'contents of source file')
        expected_contents = src_file.contents.upper()

        to_upper_transformer = StringTransformerSymbolContext.of_primitive(
            'TRANSFORMER_SYMBOL',
            string_transformers.to_uppercase(),
        )

        str_trans__unused = StringTransformerSymbolReferenceAbsStx('UNUSED_TRANSFORMER')
        transformation_w_infix_op = str_trans_abs_stx.StringTransformerCompositionAbsStx(
            [
                to_upper_transformer.abs_stx_of_reference,
                str_trans__unused,
            ],
            within_parens=False,
            allow_elements_on_separate_lines=False,
        )
        expected_remaining_tokens = TokenSequence.concat([
            TokenSequence.singleton(str_trans_abs_stx.names.SEQUENCE_OPERATOR_NAME),
            str_trans__unused.tokenization(),
        ])
        expected_remaining_source = expected_remaining_tokens.layout(the_layout)

        file_contents_syntax = string_source_abs_stx.TransformedStringSourceAbsStx(
            string_source_abs_stx.StringSourceOfFileAbsStx(
                src_rel_opt_conf.path_abs_stx_of_name(src_file.name)
            ),
            transformation_w_infix_op
        )
        checker = integration_check.checker(parse_check.rel_opts_conf_of_single(src_rel_opt_conf.relativity))
        # ACT & ASSERT #
        checker.check__abs_stx(
            self,
            file_contents_syntax,
            None,
            arrangement_w_tcds(
                tcds_contents=src_rel_opt_conf.populator_for_relativity_option_root(
                    fs.DirContents([src_file])
                ),
                symbols=to_upper_transformer.symbol_table
            ),
            Expectation.of_prim__const(
                parse=ParseExpectation(
                    source=asrt_source.source_is_not_at_end(
                        remaining_source=asrt.equals(expected_remaining_source)
                    ),
                    symbol_references=to_upper_transformer.references_assertion,
                ),
                primitive=asrt_string_source.pre_post_freeze__matches_str__const(
                    expected_contents,
                    may_depend_on_external_resources=True,
                )
            ),
            the_layout
        )
