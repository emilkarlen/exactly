import unittest

from exactly_lib.definitions.test_case import reserved_words
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.tcfs.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.tcfs.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.type_val_deps.types.path import path_ddvs, path_sdvs
from exactly_lib.type_val_deps.types.path.rel_opts_configuration import RelOptionsConfiguration
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.impls.types.path.test_resources import Arrangement, Expectation, ARG_CONFIG_FOR_ALL_RELATIVITIES, \
    Arrangement2
from exactly_lib_test.impls.types.path.test_resources import CHECKER, RelOptionArgumentConfigurationWoSuffixRequirement
from exactly_lib_test.section_document.element_parsers.test_resources.token_stream_assertions import \
    assert_token_stream, \
    assert_token_string_is
from exactly_lib_test.test_resources.source import layout
from exactly_lib_test.test_resources.source.abstract_syntax_impls import CustomAbsStx, WithinParensAbsStx
from exactly_lib_test.test_resources.source.layout import LayoutSpec
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntax import PathSymbolReferenceAbsStx, \
    PathAbsStx
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntaxes import PathStringAbsStx, \
    RelOptPathAbsStx, DefaultRelPathAbsStx, PathWConstNameAbsStx
from exactly_lib_test.type_val_deps.types.path.test_resources.sdv_assertions import equals_path_sdv_2


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestValidSyntax),
        unittest.makeSuite(TestInvalidSyntax),
        unittest.makeSuite(TestValidSyntaxOfParseViaParser),
    ])


class SourceCase:
    def __init__(self,
                 path_source: PathAbsStx,
                 after_path_expr: str,
                 source_after_parse: Assertion[TokenStream],
                 ):
        self.path_source = path_source
        self.after_path_expr = after_path_expr
        self.source_after_parse = source_after_parse


class TestValidSyntaxOfParseViaParser(unittest.TestCase):
    def test_WHEN_no_relativity_option_is_given_THEN_default_relativity_SHOULD_be_used(self):
        file_name_argument = 'file-name'
        plain_path_syntax = DefaultRelPathAbsStx(file_name_argument)
        default_and_accepted_options_variants = [
            (RelOptionType.REL_HDS_CASE,
             {RelOptionType.REL_HDS_CASE, RelOptionType.REL_ACT}),
            (RelOptionType.REL_RESULT,
             {RelOptionType.REL_RESULT, RelOptionType.REL_TMP}),
        ]
        for default_option, accepted_options in default_and_accepted_options_variants:
            expected_path = path_ddvs.of_rel_option(default_option,
                                                    path_ddvs.constant_path_part(file_name_argument))
            expected_path_value = path_sdvs.constant(expected_path)
            arg_config = RelOptionArgumentConfigurationWoSuffixRequirement(
                RelOptionsConfiguration(
                    PathRelativityVariants(accepted_options, True),
                    default_option),
                'argument_syntax_name')
            for path_suffix_is_required in [False, True]:
                with self.subTest(path_suffix_is_required=path_suffix_is_required,
                                  default_relativity=default_option):
                    CHECKER.check__abs_stx__source_variants(
                        self,
                        WithinParensAbsStx(plain_path_syntax),
                        Arrangement2(arg_config.config_for(path_suffix_is_required)),
                        equals_path_sdv_2(expected_path_value),
                    )

    def test_parse_with_relativity_option_and_relative_path_suffix(self):
        file_name_argument = 'file-name'
        for rel_option_type, rel_option_info in REL_OPTIONS_MAP.items():
            plain_path_syntax = PathWConstNameAbsStx.of_rel_opt(rel_option_type, file_name_argument)
            expected_path = path_ddvs.of_rel_option(rel_option_type,
                                                    path_ddvs.constant_path_part(file_name_argument))
            expected_path_sdv = path_sdvs.constant(expected_path)
            for path_suffix_is_required in [False, True]:
                with self.subTest(rel_option=rel_option_info.informative_name,
                                  path_suffix_is_required=path_suffix_is_required):
                    CHECKER.check__abs_stx__source_variants(
                        self,
                        WithinParensAbsStx(plain_path_syntax),
                        Arrangement2(ARG_CONFIG_FOR_ALL_RELATIVITIES.config_for(path_suffix_is_required)),
                        equals_path_sdv_2(expected_path_sdv),
                    )

    def test_file_name_of_quoted_reserved_word_is_accepted(self):
        # ARRANGE #
        default_option = RelOptionType.REL_HDS_CASE

        accepted_options = {RelOptionType.REL_HDS_CASE, RelOptionType.REL_ACT}

        arg_config = RelOptionArgumentConfigurationWoSuffixRequirement(
            RelOptionsConfiguration(
                PathRelativityVariants(accepted_options, True),
                default_option),
            'argument_syntax_name')

        for reserved_word in reserved_words.RESERVED_TOKENS:
            for quote_type in QuoteType:
                plain_path_syntax = DefaultRelPathAbsStx(reserved_word, quote_type)
                expected_path = path_ddvs.of_rel_option(default_option,
                                                        path_ddvs.constant_path_part(reserved_word))
                expected_path_value = path_sdvs.constant(expected_path)
                for path_suffix_is_required in [False, True]:
                    with self.subTest(path_suffix_is_required=path_suffix_is_required,
                                      reserved_word=reserved_word,
                                      quote_type=quote_type):
                        # ACT & ASSERT #
                        CHECKER.check__abs_stx__source_variants(
                            self,
                            WithinParensAbsStx(plain_path_syntax),
                            Arrangement2(arg_config.config_for(path_suffix_is_required)),
                            equals_path_sdv_2(expected_path_value),
                        )


class TestValidSyntax(unittest.TestCase):
    def test_WHEN_no_relativity_option_is_given_THEN_default_relativity_SHOULD_be_used(self):
        file_name_argument = 'file-name'
        default_and_accepted_options_variants = [
            (RelOptionType.REL_HDS_CASE,
             {RelOptionType.REL_HDS_CASE, RelOptionType.REL_ACT}),
            (RelOptionType.REL_RESULT,
             {RelOptionType.REL_RESULT, RelOptionType.REL_TMP}),
        ]
        for default_option, accepted_options in default_and_accepted_options_variants:
            expected_path = path_ddvs.of_rel_option(default_option,
                                                    path_ddvs.constant_path_part(file_name_argument))
            expected_path_value = path_sdvs.constant(expected_path)
            arg_config = RelOptionArgumentConfigurationWoSuffixRequirement(
                RelOptionsConfiguration(
                    PathRelativityVariants(accepted_options, True),
                    default_option),
                'argument_syntax_name')
            source_cases = [
                SourceCase(
                    DefaultRelPathAbsStx(file_name_argument),
                    '',
                    assert_token_stream(is_null=asrt.is_true)),
                SourceCase(
                    DefaultRelPathAbsStx(file_name_argument),
                    'arg3',
                    assert_token_stream(is_null=asrt.is_false,
                                        head_token=assert_token_string_is('arg3')
                                        )
                ),
            ]
            for source_case in source_cases:
                source_tokens = _source_token_sequence(source_case.path_source, source_case.after_path_expr)
                source_str = source_tokens.layout(LayoutSpec.of_default())

                for path_suffix_is_required in [False, True]:
                    with self.subTest(path_expr_source=source_case.path_source,
                                      after_path_expr=source_case.after_path_expr,
                                      path_suffix_is_required=path_suffix_is_required):
                        CHECKER.check(
                            self,
                            Arrangement(source_str,
                                        arg_config.config_for(path_suffix_is_required)),
                            Expectation(expected_path_value,
                                        source_case.source_after_parse)
                        )

    def test_parse_with_relativity_option_and_relative_path_suffix(self):
        file_name_argument = 'file-name'
        for rel_option_type, rel_option_info in REL_OPTIONS_MAP.items():
            source_cases = [
                SourceCase(
                    PathWConstNameAbsStx.of_rel_opt(rel_option_type, file_name_argument),
                    '',
                    assert_token_stream(is_null=asrt.is_true),
                ),
                SourceCase(
                    PathWConstNameAbsStx.of_rel_opt(rel_option_type, file_name_argument),
                    'arg3 arg4',
                    assert_token_stream(is_null=asrt.is_false,
                                        head_token=assert_token_string_is('arg3')
                                        ),
                ),
            ]
            for source_case in source_cases:
                expected_path = path_ddvs.of_rel_option(rel_option_type,
                                                        path_ddvs.constant_path_part(file_name_argument))
                expected_path_sdv = path_sdvs.constant(expected_path)
                source_tokens = _source_token_sequence(source_case.path_source, source_case.after_path_expr)
                source_str = source_tokens.layout(LayoutSpec.of_default())
                for path_suffix_is_required in [False, True]:
                    with self.subTest(rel_option=rel_option_info.informative_name,
                                      after_path_expr=source_case.after_path_expr,
                                      path_suffix_is_required=path_suffix_is_required):
                        CHECKER.check(
                            self,
                            Arrangement(source_str,
                                        ARG_CONFIG_FOR_ALL_RELATIVITIES.config_for(path_suffix_is_required)),
                            Expectation(expected_path_sdv,
                                        source_case.source_after_parse))


def _source_token_sequence(path_source: PathAbsStx, after_path_expr: str) -> TokenSequence:
    path_expr = WithinParensAbsStx(
        path_source,
        end_paren_on_separate_line=False,
    )
    return TokenSequence.concat([
        path_expr.tokenization(),
        TokenSequence.singleton(after_path_expr),
    ])


class TestInvalidSyntax(unittest.TestCase):
    def test_fail_when_missing_end_end_paren(self):
        cases = [
            NameAndValue(
                'reference',
                PathSymbolReferenceAbsStx('PATH_SYMBOL'),
            ),
            NameAndValue(
                'plain string',
                PathStringAbsStx.of_plain_str('file.txt'),
            ),
            NameAndValue(
                'w relativity',
                RelOptPathAbsStx(RelOptionType.REL_RESULT, 'file.txt'),
            ),
            NameAndValue(
                'missing path',
                CustomAbsStx.empty(),
            ),
        ]
        for case in cases:
            missing_end_paren = CustomAbsStx(
                TokenSequence.concat([
                    TokenSequence.singleton('('),
                    TokenSequence.optional_new_line(),
                    case.value.tokenization(),
                ])
            )
            tokens = missing_end_paren.tokenization()
            for layout_case in layout.STANDARD_LAYOUT_SPECS:
                source_str = tokens.layout(layout_case.value)
                CHECKER.assert_raises_invalid_argument_exception(
                    self,
                    source_str,
                    layout_case.name,
                )

    def test_fail_when_missing_path(self):
        cases = [
            NameAndValue(
                'empty',
                CustomAbsStx.empty(),
            ),
            NameAndValue(
                'missing file name',
                RelOptPathAbsStx(RelOptionType.REL_RESULT, ''),
            ),
        ]
        for case in cases:
            missing_end_paren = WithinParensAbsStx(case.value)
            tokens = missing_end_paren.tokenization()
            for layout_case in layout.STANDARD_LAYOUT_SPECS:
                source_str = tokens.layout(layout_case.value)
                CHECKER.assert_raises_invalid_argument_exception(
                    self,
                    source_str,
                    layout_case.name,
                    path_suffix_is_required_cases=(True,)
                )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
