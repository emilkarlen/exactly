import unittest
from pathlib import Path, PurePosixPath

from exactly_lib.definitions.path import REL_SYMBOL_OPTION_NAME, REL_TMP_OPTION, REL_CWD_OPTION, \
    REL_HDS_CASE_OPTION_NAME
from exactly_lib.definitions.test_case import reserved_words
from exactly_lib.impls.types.path import parse_path as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.tcfs.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.tcfs.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.value_restrictions import PathAndRelativityRestriction
from exactly_lib.type_val_deps.types.path import path_ddvs, path_sdvs, path_relativities
from exactly_lib.type_val_deps.types.path import path_part_sdvs
from exactly_lib.type_val_deps.types.path import references
from exactly_lib.type_val_deps.types.path.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import HARD_QUOTE_CHAR, SOFT_QUOTE_CHAR, QuoteType
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.impls.types.parse.test_resources.source_case import SourceCase
from exactly_lib_test.impls.types.path.test_resources import Arrangement, Expectation, Expectation2, \
    RelOptionArgumentConfigurationWoSuffixRequirement, ArrangementWoSuffixRequirement, ARBITRARY_REL_OPT_ARG_CONF, \
    ARG_CONFIG_FOR_ALL_RELATIVITIES, arg_config_with_all_accepted_and_default, arg_config_for_rel_symbol_config, \
    option_string_for, option_string_for_relativity, expect, Arrangement2
from exactly_lib_test.impls.types.path.test_resources import CHECKER
from exactly_lib_test.section_document.element_parsers.test_resources.token_stream_assertions import \
    assert_token_stream, \
    assert_token_string_is
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.symbol.test_resources.symbol_syntax import NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.tcfs.test_resources import format_rel_option
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import \
    data_restrictions_assertions as asrt_w_str_rend_rest
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.symbol_reference_assertions import \
    is_reference_to_string__w_all_indirect_refs_are_strings
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources import symbol_context as file_matcher
from exactly_lib_test.type_val_deps.types.list_.test_resources import symbol_context as list_
from exactly_lib_test.type_val_deps.types.path.test_resources import sdv_assertions as asrt_path_sdv
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntaxes import RelSymbolPathAbsStx, \
    RelOptPathAbsStx, DefaultRelPathAbsStx
from exactly_lib_test.type_val_deps.types.path.test_resources.path_part_assertions import equals_path_part_string
from exactly_lib_test.type_val_deps.types.path.test_resources.references import path_or_string_reference_restrictions
from exactly_lib_test.type_val_deps.types.path.test_resources.sdv_assertions import equals_path_sdv, matches_path_sdv
from exactly_lib_test.type_val_deps.types.path.test_resources.symbol_context import PathDdvSymbolContext, \
    ConstantSuffixPathDdvSymbolContext, PathSymbolContext
from exactly_lib_test.type_val_deps.types.program.test_resources import symbol_context as program
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources import symbol_context as st_symbol_context


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()

    ret_val.addTest(unittest.makeSuite(TestFailingParseDueToInvalidSyntax))

    ret_val.addTest(unittest.makeSuite(TestParseWithoutRelSymbolRelativity))
    ret_val.addTest(unittest.makeSuite(TestParseWithRelSymbolRelativity))

    ret_val.addTest(unittest.makeSuite(TestParseWithSymbolReferenceEmbeddedInPathArgument))

    ret_val.addTest(unittest.makeSuite(TestParseWithMandatoryPathSuffix))
    ret_val.addTest(unittest.makeSuite(TestParseWithOptionalPathSuffix))

    ret_val.addTest(unittest.makeSuite(TestParseFromParseSource))
    ret_val.addTest(unittest.makeSuite(TestParsesCorrectValueFromParseSource))

    ret_val.addTest(unittest.makeSuite(TestTypeMustBeEitherPathOrStringErrMsgGenerator))

    ret_val.addTest(unittest.makeSuite(TestRelativityOfSourceFileLocation))

    ret_val.addTest(TestAQuotedReservedWordIsAnAcceptedFileName())

    return ret_val


class TestParsesBase(unittest.TestCase):
    def _check(self,
               arrangement: Arrangement,
               expectation: Expectation):
        CHECKER.check(self, arrangement, expectation)

    def _check2(self,
                arrangement: Arrangement,
                expectation: Expectation2):
        CHECKER.check2(self, arrangement, expectation)

    def _assert_raises_invalid_argument_exception(self,
                                                  source_string: str,
                                                  test_name: str = ''):
        CHECKER.assert_raises_invalid_argument_exception(self, source_string, test_name)


class TestFailingParseDueToInvalidSyntax(TestParsesBase):
    def test_fail_due_to_invalid_file_name(self):
        invalid_file_names = (
                [
                    SOFT_QUOTE_CHAR + 'file-name',
                    HARD_QUOTE_CHAR + 'file-name',
                ] +
                list(reserved_words.RESERVED_TOKENS)
        )
        path_variant_cases = [
            NameAndValue(
                'default relativity',
                lambda fn: DefaultRelPathAbsStx(fn),
            ),
            NameAndValue(
                'relative symbol',
                lambda fn: RelSymbolPathAbsStx('SYMBOL_NAME', fn),
            ),
            NameAndValue(
                'relative option',
                lambda fn: RelOptPathAbsStx(RelOptionType.REL_ACT, fn),
            ),
        ]
        for path_variant_case in path_variant_cases:
            for invalid_file_name in invalid_file_names:
                with self.subTest(path_variant=path_variant_case.name,
                                  invalid_file_name=repr(invalid_file_name)):
                    source_syntax = path_variant_case.value(invalid_file_name)
                    source_str = source_syntax.as_str__default()
                    self._assert_raises_invalid_argument_exception(source_str,
                                                                   test_name=repr(source_str))

    def test_fail_due_to_invalid_symbol_name(self):
        invalid_path_syntax = RelSymbolPathAbsStx(NOT_A_VALID_SYMBOL_NAME, 'valid-file-name')
        source_str = invalid_path_syntax.as_str__default()
        self._assert_raises_invalid_argument_exception(source_str,
                                                       test_name=repr(source_str))


class TestAQuotedReservedWordIsAnAcceptedFileName(TestParsesBase):
    def runTest(self):
        invalid_file_names = reserved_words.RESERVED_TOKENS

        arg_config = RelOptionArgumentConfigurationWoSuffixRequirement(
            RelOptionsConfiguration(
                PathRelativityVariants(RelOptionType, True),
                RelOptionType.REL_HDS_CASE),
            'argument_syntax_name')

        path_symbol = PathSymbolContext.of_arbitrary_value('PATH_SYMBOL')
        path_variant_cases = [
            NameAndValue(
                'default relativity',
                lambda fn, qt: DefaultRelPathAbsStx(fn, qt),
            ),
            NameAndValue(
                'relative symbol',
                lambda fn, qt: RelSymbolPathAbsStx(path_symbol.name, fn, qt),
            ),
            NameAndValue(
                'relative option',
                lambda fn, qt: RelOptPathAbsStx(RelOptionType.REL_ACT, fn, qt),
            ),
        ]
        for invalid_file_name in invalid_file_names:
            path_expectation = asrt_path_sdv.NameMatches(path_symbol.symbol_table,
                                                         asrt.equals(invalid_file_name))
            for path_suffix_is_required in [False, True]:
                arrangement = Arrangement2(arg_config.config_for(path_suffix_is_required))
                for path_variant_case in path_variant_cases:
                    for quote_type in QuoteType:
                        source_syntax = path_variant_case.value(invalid_file_name, quote_type)
                        with self.subTest(path_variant=path_variant_case.name,
                                          invalid_file_name=repr(invalid_file_name),
                                          quote_type=quote_type):
                            CHECKER.check__abs_stx__source_variants(
                                self,
                                source_syntax,
                                arrangement,
                                path_expectation,
                            )


class TestParseWithoutRelSymbolRelativity(TestParsesBase):
    def test_fail_when_no_arguments(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_path(TokenStream(''),
                           ARG_CONFIG_FOR_ALL_RELATIVITIES.config_for(True))

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
            source_and_token_stream_assertion_variants = [
                (
                    '{file_name_argument} arg3 arg4',
                    assert_token_stream(is_null=asrt.is_false,
                                        head_token=assert_token_string_is('arg3')
                                        )
                ),
                (
                    '{file_name_argument}',
                    assert_token_stream(is_null=asrt.is_true)
                ),
                (
                    '    {file_name_argument}',
                    assert_token_stream(is_null=asrt.is_true)
                ),
                (
                    '{file_name_argument}\nnext line',
                    assert_token_stream(is_null=asrt.is_false,
                                        head_token=assert_token_string_is('next'))
                ),
            ]
            for source, token_stream_assertion in source_and_token_stream_assertion_variants:
                for path_suffix_is_required in [False, True]:
                    with self.subTest(msg='source=' + repr(source) +
                                          ' / path_suffix_is_required=' + str(path_suffix_is_required)):
                        argument_string = source.format(file_name_argument=file_name_argument)
                        self._check(
                            Arrangement(argument_string,
                                        arg_config.config_for(path_suffix_is_required)),
                            Expectation(expected_path_value,
                                        token_stream_assertion)
                        )

    def test_parse_with_relativity_option_and_relative_path_suffix(self):
        file_name_argument = 'file-name'
        for rel_option_type, rel_option_info in REL_OPTIONS_MAP.items():
            expected_path = path_ddvs.of_rel_option(rel_option_type,
                                                    path_ddvs.constant_path_part(file_name_argument))
            expected_path_sdv = path_sdvs.constant(expected_path)
            option_str = option_string_for(rel_option_info._option_name)
            source_and_token_stream_assertion_variants = [
                (
                    '{option_str} {file_name_argument} arg3 arg4',
                    assert_token_stream(is_null=asrt.is_false,
                                        head_token=assert_token_string_is('arg3')
                                        )
                ),
                (
                    '{option_str} {file_name_argument}',
                    assert_token_stream(is_null=asrt.is_true)
                ),
                (
                    '   {option_str}    {file_name_argument}',
                    assert_token_stream(is_null=asrt.is_true)
                ),
                (
                    '{option_str} {file_name_argument}\nnext line',
                    assert_token_stream(is_null=asrt.is_false,
                                        head_token=assert_token_string_is('next'))
                ),
            ]
            for source, token_stream_assertion in source_and_token_stream_assertion_variants:
                for path_suffix_is_required in [False, True]:
                    with self.subTest(msg=rel_option_info.informative_name +
                                          ' / path_suffix_is_required=' + str(path_suffix_is_required)):
                        argument_string = source.format(option_str=option_str,
                                                        file_name_argument=file_name_argument)
                        self._check(
                            Arrangement(argument_string,
                                        ARG_CONFIG_FOR_ALL_RELATIVITIES.config_for(path_suffix_is_required)),
                            Expectation(expected_path_sdv,
                                        token_stream_assertion))

    def test_parse_with_relativity_option_and_absolute_path_suffix(self):
        file_name_argument = '/an/absolute/path'
        for rel_option_type, rel_option_info in REL_OPTIONS_MAP.items():
            expected_path = path_ddvs.absolute_file_name(file_name_argument)
            expected_path_sdv = path_sdvs.constant(expected_path)
            option_str = option_string_for(rel_option_info._option_name)
            source_and_token_stream_assertion_variants = [
                (
                    '{option_str} {file_name_argument} arg3 arg4',
                    assert_token_stream(is_null=asrt.is_false,
                                        head_token=assert_token_string_is('arg3')
                                        )
                ),
                (
                    '{option_str} {file_name_argument}',
                    assert_token_stream(is_null=asrt.is_true)
                ),
                (
                    '   {option_str}    {file_name_argument}',
                    assert_token_stream(is_null=asrt.is_true)
                ),
                (
                    '{option_str} {file_name_argument}\nnext line',
                    assert_token_stream(is_null=asrt.is_false,
                                        head_token=assert_token_string_is('next'))
                ),
            ]
            for source, token_stream_assertion in source_and_token_stream_assertion_variants:
                for path_suffix_is_required in [False, True]:
                    with self.subTest(msg=rel_option_info.informative_name +
                                          ' / path_suffix_is_required=' + str(path_suffix_is_required)):
                        argument_string = source.format(option_str=option_str,
                                                        file_name_argument=file_name_argument)
                        self._check(
                            Arrangement(argument_string,
                                        ARG_CONFIG_FOR_ALL_RELATIVITIES.config_for(path_suffix_is_required)),
                            Expectation(expected_path_sdv,
                                        token_stream_assertion))

    def test_parse_with_only_absolute_path_suffix(self):
        file_name_argument = '/an/absolute/path'
        expected_path = path_ddvs.absolute_file_name(file_name_argument)
        expected_path_sdv = path_sdvs.constant(expected_path)
        source_and_token_stream_assertion_variants = [
            (
                '{file_name_argument} arg3 arg4',
                assert_token_stream(is_null=asrt.is_false,
                                    head_token=assert_token_string_is('arg3')
                                    )
            ),
            (
                '{file_name_argument}',
                assert_token_stream(is_null=asrt.is_true)
            ),
            (
                '      {file_name_argument}',
                assert_token_stream(is_null=asrt.is_true)
            ),
            (
                '{file_name_argument}\nnext line',
                assert_token_stream(is_null=asrt.is_false,
                                    head_token=assert_token_string_is('next'))
            ),
        ]
        for source, token_stream_assertion in source_and_token_stream_assertion_variants:
            for path_suffix_is_required in [False, True]:
                argument_string = source.format(file_name_argument=file_name_argument)
                with self.subTest(msg='path_suffix_is_required={}, source="{}"'.format(path_suffix_is_required,
                                                                                       argument_string)):
                    self._check(
                        Arrangement(argument_string,
                                    ARG_CONFIG_FOR_ALL_RELATIVITIES.config_for(path_suffix_is_required)),
                        Expectation(expected_path_sdv,
                                    token_stream_assertion))

    def test_WHEN_relativity_option_is_not_one_of_accepted_options_THEN_parse_SHOULD_fail(self):
        file_name_argument = 'file-name'
        used_and_default_and_accepted_options_variants = [
            (
                RelOptionType.REL_ACT,
                RelOptionType.REL_HDS_CASE,
                {RelOptionType.REL_HDS_CASE}
            ),
            (
                RelOptionType.REL_HDS_CASE,
                RelOptionType.REL_ACT,
                {RelOptionType.REL_TMP}
            ),
        ]

        for used_option, default_option, accepted_options in used_and_default_and_accepted_options_variants:
            for path_suffix_is_required in [False, True]:
                option_str = option_string_for(REL_OPTIONS_MAP[used_option]._option_name)
                arg_config = RelOptionArgumentConfiguration(
                    RelOptionsConfiguration(
                        PathRelativityVariants(accepted_options, True),
                        default_option),
                    'argument_syntax_name',
                    path_suffix_is_required)
                source_variants = [
                    '{option_str} {file_name_argument} arg3 arg4',
                    '{option_str} {file_name_argument}',
                    '   {option_str}    {file_name_argument}',
                    '{option_str} {file_name_argument}\nnext line',
                ]
                for source in source_variants:
                    with self.subTest(msg='used_option={} source={}'.format(option_str, repr(source))):
                        argument_string = source.format(option_str=option_str,
                                                        file_name_argument=file_name_argument)
                        token_stream = TokenStream(argument_string)
                        with self.assertRaises(SingleInstructionInvalidArgumentException):
                            sut.parse_path(token_stream, arg_config)

    def test_parse_with_option_fails_when_no_file_argument(self):
        for rel_option_info in REL_OPTIONS_MAP.values():
            with self.subTest(msg=rel_option_info.informative_name):
                option_str = option_string_for(rel_option_info._option_name)
                ts = TokenStream(option_str)
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_path(ts, ARG_CONFIG_FOR_ALL_RELATIVITIES.config_for(True))


class TestParseWithRelSymbolRelativity(TestParsesBase):
    def test_WHEN_symbol_name_is_invalid_THEN_parse_SHOULD_fail(self):
        rel_symbol_option = option_string_for(REL_SYMBOL_OPTION_NAME)
        cases = [
            '{rel_symbol_option} INVALID_SYMBOL_NAME? file_name'.format(rel_symbol_option=rel_symbol_option),
            '{rel_symbol_option} ?INVALID_SYMBOL_NAME file_name'.format(rel_symbol_option=rel_symbol_option),
            '{rel_symbol_option} -invalid_symbol_name file_name'.format(rel_symbol_option=rel_symbol_option),
            '{rel_symbol_option} {soft_quote}invalid_symbol_name{soft_quote} file_name'.format(
                rel_symbol_option=rel_symbol_option,
                soft_quote=SOFT_QUOTE_CHAR),
            '{rel_symbol_option} ?? file_name'.format(rel_symbol_option=rel_symbol_option),
        ]
        for source_string in cases:
            self._assert_raises_invalid_argument_exception(source_string,
                                                           test_name=source_string)

    def test_WHEN_rel_symbol_option_is_quoted_THEN_parse_SHOULD_treat_that_string_as_file_name(self):
        rel_symbol_option = option_string_for(REL_SYMBOL_OPTION_NAME)
        source = '"{rel_symbol_option}" SYMBOL_NAME file_name'.format(rel_symbol_option=rel_symbol_option)
        expected_path = path_ddvs.of_rel_option(ARG_CONFIG_FOR_ALL_RELATIVITIES.options.default_option,
                                                path_ddvs.constant_path_part('{rel_symbol_option}'.format(
                                                    rel_symbol_option=rel_symbol_option)))
        expected_path_value = path_sdvs.constant(expected_path)
        for path_suffix_is_required in [False, True]:
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                self._check(
                    Arrangement(source,
                                path_relativities.all_rel_options_arg_config('ARG-SYNTAX-NAME',
                                                                             path_suffix_is_required)),
                    Expectation(expected_path_value,
                                assert_token_stream(head_token=assert_token_string_is('SYMBOL_NAME')))
                )

    def test_WHEN_no_file_name_argument_is_given_and_path_suffix_is_required_THEN_parse_SHOULD_fail(self):
        rel_symbol_option = option_string_for(REL_SYMBOL_OPTION_NAME)
        source = '{rel_symbol_option} SYMBOL_NAME'.format(rel_symbol_option=rel_symbol_option)
        token_stream = TokenStream(source)
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_path(token_stream,
                           path_relativities.all_rel_options_arg_config('ARG-SYNTAX-NAME', True))

    def test_WHEN_no_file_name_argument_is_given_and_path_suffix_is_not_required_THEN_parse_SHOULD_succeed(self):
        rel_symbol_option = option_string_for(REL_SYMBOL_OPTION_NAME)
        source = '{rel_symbol_option} SYMBOL_NAME'.format(rel_symbol_option=rel_symbol_option)
        token_stream = TokenStream(source)
        sut.parse_path(token_stream,
                       path_relativities.all_rel_options_arg_config('ARG-SYNTAX-NAME', False))

    def test_reference_restrictions_on_symbol_references_in_path_suffix_SHOULD_be_string_restrictions(self):
        rel_symbol_option = option_string_for(REL_SYMBOL_OPTION_NAME)
        defined_path_symbol = ConstantSuffixPathDdvSymbolContext(
            'DEFINED_PATH_SYMBOL',
            RelOptionType.REL_TMP,
            'DEFINED_PATH_SYMBOL_VALUE',
            PathRelativityVariants({RelOptionType.REL_HDS_CASE,
                                    RelOptionType.REL_TMP},
                                   True),
        )
        suffix_symbol = StringConstantSymbolContext('PATH_SUFFIX_SYMBOL', 'symbol-string-value')

        suffix_string_constant = ' string constant'
        test_cases = [
            ('Symbol reference in path suffix '
             'SHOULD '
             'become a symbol reference that must be a string',
             ArrangementWoSuffixRequirement(
                 source='{rel_symbol_option} {defined_path_symbol} {suffix_symbol_reference}'.format(
                     rel_symbol_option=rel_symbol_option,
                     defined_path_symbol=defined_path_symbol.name,
                     suffix_symbol_reference=suffix_symbol.name__sym_ref_syntax),
                 rel_option_argument_configuration=arg_config_for_rel_symbol_config(
                     defined_path_symbol.value.accepted_relativities,
                     RelOptionType.REL_HDS_CASE),
             ),
             expect(
                 resolved_path=
                 path_ddvs.of_rel_option(
                     defined_path_symbol.rel_option_type,
                     path_ddvs.constant_path_part(
                         str(defined_path_symbol.path_suffix_path / Path(suffix_symbol.str_value)))),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     defined_path_symbol.reference_assertion__path,
                     suffix_symbol.reference_assertion__string__w_all_indirect_refs_are_strings,
                 ]),
                 symbol_table=
                 SymbolContext.symbol_table_of_contexts([
                     defined_path_symbol,
                     suffix_symbol,
                 ]),
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )
             ),
            ('Symbol reference and string constant in path suffix, inside soft quotes'
             'SHOULD '
             'become a symbol reference that must be a string',
             ArrangementWoSuffixRequirement(
                 source='{rel_symbol_option} {defined_path_symbol} '
                        '{soft_quote}{suffix_symbol_reference}{suffix_string_constant}{soft_quote}'.format(
                     rel_symbol_option=rel_symbol_option,
                     soft_quote=SOFT_QUOTE_CHAR,
                     defined_path_symbol=defined_path_symbol.name,
                     suffix_symbol_reference=suffix_symbol.name__sym_ref_syntax,
                     suffix_string_constant=suffix_string_constant),
                 rel_option_argument_configuration=arg_config_for_rel_symbol_config(
                     defined_path_symbol.value.accepted_relativities,
                     RelOptionType.REL_HDS_CASE
                 ),
             ),
             expect(
                 resolved_path=
                 path_ddvs.of_rel_option(
                     defined_path_symbol.rel_option_type,
                     path_ddvs.constant_path_part(
                         str(defined_path_symbol.path_suffix_path /
                             Path(suffix_symbol.str_value + suffix_string_constant)))),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     defined_path_symbol.reference_assertion__path,
                     suffix_symbol.reference_assertion__string__w_all_indirect_refs_are_strings,
                 ]),
                 symbol_table=
                 SymbolContext.symbol_table_of_contexts([
                     defined_path_symbol,
                     suffix_symbol,
                 ]),
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )
             ),
        ]
        for test_name, arrangement, expectation in test_cases:
            for path_suffix_is_required in [False, True]:
                with self.subTest(test_name=test_name,
                                  path_suffix_is_required=path_suffix_is_required):
                    self._check2(arrangement.for_path_suffix_required(path_suffix_is_required),
                                 expectation)

    def test_consumption_of_source(self):
        file_name_argument = 'file-name'
        symbol_name = 'symbol_NAME'
        option_str = option_string_for(REL_SYMBOL_OPTION_NAME)
        source_and_token_stream_assertion_variants = [
            (
                '{option_str} {symbol_name} {file_name_argument} arg3 arg4',
                assert_token_stream(is_null=asrt.is_false,
                                    head_token=assert_token_string_is('arg3')
                                    )
            ),
            (
                '{option_str} {symbol_name} {file_name_argument}',
                assert_token_stream(is_null=asrt.is_true)
            ),
            (
                '   {option_str}   {symbol_name}  {file_name_argument}',
                assert_token_stream(is_null=asrt.is_true)
            ),
            (
                '{option_str} {symbol_name}  {file_name_argument}\nnext line',
                assert_token_stream(is_null=asrt.is_false,
                                    head_token=assert_token_string_is('next'))
            ),
        ]
        for source, token_stream_assertion in source_and_token_stream_assertion_variants:
            accepted_relativities_variants = [
                PathRelativityVariants({RelOptionType.REL_ACT}, True),
                PathRelativityVariants({RelOptionType.REL_ACT}, False),
                PathRelativityVariants({RelOptionType.REL_ACT, RelOptionType.REL_HDS_CASE}, False),
            ]
            for accepted_relativities in accepted_relativities_variants:
                expected_symbol_reference = SymbolReference(symbol_name,
                                                            ReferenceRestrictionsOnDirectAndIndirect(
                                                                PathAndRelativityRestriction(
                                                                    accepted_relativities)))
                expected_path_sdv = path_sdvs.rel_symbol(expected_symbol_reference,
                                                         path_part_sdvs.from_constant_str(
                                                             file_name_argument))
                for path_suffix_is_required in [False, True]:
                    arg_config = arg_config_for_rel_symbol_config(accepted_relativities)
                    test_descr = 'path_suffix_is_required={} / source={}'.format(path_suffix_is_required,
                                                                                 repr(source))
                    with self.subTest(msg=test_descr):
                        argument_string = source.format(option_str=option_str,
                                                        symbol_name=symbol_name,
                                                        file_name_argument=file_name_argument)
                        self._check(
                            Arrangement(argument_string,
                                        arg_config.config_for(path_suffix_is_required)),
                            Expectation(expected_path_sdv,
                                        token_stream_assertion)
                        )


class TestRelativityOfSourceFileLocation(TestParsesBase):
    def test_successful_parse_with_source_file_location(self):
        source_file_location_path = Path(PurePosixPath('/source/file/location'))
        constant_path_part = 'constant-path-part'
        symbol = StringConstantSymbolContext('PATH_SUFFIX_SYMBOL', 'symbol-string-value')
        fm = dict(format_rel_option.FORMAT_MAP,
                  symbol_reference=symbol.name__sym_ref_syntax,
                  constant_path_part=constant_path_part,
                  )
        accepted_relativities = arg_config_with_all_accepted_and_default(RelOptionType.REL_ACT)
        test_cases = [
            ('Constant after src-file relativity '
             'SHOULD '
             'become a abs path with constant path suffix',
             ArrangementWoSuffixRequirement(
                 source='{rel_source_file} {constant_path_part}'.format_map(fm),
                 rel_option_argument_configuration=accepted_relativities,
                 source_file_path=source_file_location_path
             ),
             expect(
                 resolved_path=
                 path_ddvs.rel_abs_path(source_file_location_path,
                                        path_ddvs.constant_path_part(constant_path_part)),
                 expected_symbol_references=
                 asrt.is_empty_sequence,
                 symbol_table=
                 empty_symbol_table(),
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )
             ),
            ('Symbol reference after src-file relativity '
             'SHOULD '
             'become a abs path with symbol reference path suffix that must be a string',
             ArrangementWoSuffixRequirement(
                 source='{rel_source_file} {symbol_reference}'.format_map(fm),
                 rel_option_argument_configuration=accepted_relativities,
                 source_file_path=source_file_location_path
             ),
             expect(
                 resolved_path=
                 path_ddvs.rel_abs_path(source_file_location_path,
                                        path_ddvs.constant_path_part(symbol.str_value)),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     symbol.reference_assertion__string__w_all_indirect_refs_are_strings,
                 ]),
                 symbol_table=
                 symbol.symbol_table,
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )
             ),
            ('Other accepted explicit relativity should be available',
             ArrangementWoSuffixRequirement(
                 source='{rel_case_home} {symbol_reference}'.format_map(fm),
                 rel_option_argument_configuration=accepted_relativities,
                 source_file_path=source_file_location_path
             ),
             expect(
                 resolved_path=
                 path_ddvs.of_rel_option(RelOptionType.REL_HDS_CASE,
                                         path_ddvs.constant_path_part(
                                             symbol.str_value)),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     symbol.reference_assertion__string__w_all_indirect_refs_are_strings,
                 ]),
                 symbol_table=
                 symbol.symbol_table,
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )
             ),
            ('Default relativity should be available',
             ArrangementWoSuffixRequirement(
                 source='{symbol_reference}'.format_map(fm),
                 rel_option_argument_configuration=accepted_relativities,
                 source_file_path=source_file_location_path
             ),
             expect(
                 resolved_path=
                 path_ddvs.of_rel_option(RelOptionType.REL_ACT,
                                         path_ddvs.constant_path_part(
                                             symbol.str_value)),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     asrt_sym_ref.matches_reference_2(
                         symbol.name,
                         asrt_w_str_rend_rest.equals__w_str_rendering(
                             path_or_string_reference_restrictions(
                                 accepted_relativities.options.accepted_relativity_variants)
                         )
                     ),
                 ]),
                 symbol_table=
                 symbol.symbol_table,
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )
             ),
        ]
        for test_name, arrangement, expectation in test_cases:
            for path_suffix_is_required in [False, True]:
                with self.subTest(msg=test_name + ' / path_suffix_is_required = ' + str(path_suffix_is_required)):
                    self._check2(arrangement.for_path_suffix_required(path_suffix_is_required),
                                 expectation)

    def test_rel_source_file_should_not_be_available_when_no_source_file_is_given(self):
        token_stream = TokenStream('{rel_source_file} suffix'.format_map(format_rel_option.FORMAT_MAP))
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            rel_opt_arg_conf = ARBITRARY_REL_OPT_ARG_CONF.config_for(False)
            sut.parse_path(token_stream,
                           rel_opt_arg_conf,
                           source_file_location=None)


class TestParseWithSymbolReferenceEmbeddedInPathArgument(TestParsesBase):
    def test_with_explicit_relativity(self):
        symbol = StringConstantSymbolContext('PATH_SUFFIX_SYMBOL', 'symbol-string-value')
        symbol_1 = StringConstantSymbolContext('SYMBOL_NAME_1', 'symbol 1 value')
        symbol_2 = StringConstantSymbolContext('SYMBOL_NAME_2', 'symbol 2 value')
        test_cases = [
            ('Symbol reference after explicit relativity '
             'SHOULD '
             'become a symbol reference path suffix that must be a string',
             ArrangementWoSuffixRequirement(
                 source='{rel_hds_case_option} {symbol_reference}'.format(
                     rel_hds_case_option=option_string_for_relativity(RelOptionType.REL_HDS_CASE),
                     symbol_reference=symbol.name__sym_ref_syntax),
                 rel_option_argument_configuration=arg_config_with_all_accepted_and_default(RelOptionType.REL_ACT),
             ),
             expect(
                 resolved_path=
                 path_ddvs.of_rel_option(RelOptionType.REL_HDS_CASE,
                                         path_ddvs.constant_path_part(
                                             symbol.str_value)),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     symbol.reference_assertion__string__w_all_indirect_refs_are_strings,
                 ]),
                 symbol_table=
                 symbol.symbol_table,
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )
             ),
            ('Mixed symbol references and constants as path suffix after explicit relativity '
             'SHOULD '
             'become a symbol reference path suffix that must be a strings',
             ArrangementWoSuffixRequirement(
                 source='{rel_tmp_option} {symbol_reference1}/const{symbol_reference2}'.format(
                     rel_tmp_option=option_string_for_relativity(RelOptionType.REL_TMP),
                     symbol_reference1=symbol_1.name__sym_ref_syntax,
                     symbol_reference2=symbol_2.name__sym_ref_syntax),
                 rel_option_argument_configuration=arg_config_with_all_accepted_and_default(RelOptionType.REL_TMP),
             ),
             expect(
                 resolved_path=
                 path_ddvs.of_rel_option(RelOptionType.REL_TMP,
                                         path_ddvs.constant_path_part(
                                             symbol_1.str_value + '/const' + symbol_2.str_value)),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     symbol_1.reference_assertion__string__w_all_indirect_refs_are_strings,
                     symbol_2.reference_assertion__string__w_all_indirect_refs_are_strings,
                 ]),
                 symbol_table=
                 SymbolContext.symbol_table_of_contexts([symbol_1, symbol_2]),
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )
             ),
            ('Mixed symbol references and constants - within soft quotes - as path suffix after explicit relativity '
             'SHOULD '
             'become a symbol reference path suffix that must be a strings',
             ArrangementWoSuffixRequirement(
                 source='{rel_tmp_option} {soft_quote}{symbol_reference1}/ const {symbol_reference2}{soft_quote}'.format(
                     soft_quote=SOFT_QUOTE_CHAR,
                     rel_tmp_option=option_string_for_relativity(RelOptionType.REL_TMP),
                     symbol_reference1=symbol_1.name__sym_ref_syntax,
                     symbol_reference2=symbol_2.name__sym_ref_syntax),
                 rel_option_argument_configuration=arg_config_with_all_accepted_and_default(RelOptionType.REL_TMP),
             ),
             expect(
                 resolved_path=
                 path_ddvs.of_rel_option(RelOptionType.REL_TMP,
                                         path_ddvs.constant_path_part(
                                             symbol_1.str_value + '/ const ' + symbol_2.str_value)),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     symbol_1.reference_assertion__string__w_all_indirect_refs_are_strings,
                     symbol_2.reference_assertion__string__w_all_indirect_refs_are_strings,
                 ]),
                 symbol_table=
                 SymbolContext.symbol_table_of_contexts([symbol_1, symbol_2]),
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )),
            ('Hard quoted symbol reference after explicit relativity'
             ' SHOULD '
             'become a path suffix that is the literal quoted symbol reference',
             ArrangementWoSuffixRequirement(
                 source='{rel_hds_case_option} {hard_quote}{symbol_reference}{hard_quote}'.format(
                     rel_hds_case_option=option_string_for_relativity(RelOptionType.REL_HDS_CASE),
                     hard_quote=HARD_QUOTE_CHAR,
                     symbol_reference=symbol.name__sym_ref_syntax),
                 rel_option_argument_configuration=arg_config_with_all_accepted_and_default(RelOptionType.REL_ACT),
             ),
             expect(
                 resolved_path=
                 path_ddvs.of_rel_option(
                     RelOptionType.REL_HDS_CASE,
                     path_ddvs.constant_path_part(symbol.name__sym_ref_syntax)),
                 expected_symbol_references=
                 asrt.equals([]),
                 symbol_table=
                 empty_symbol_table(),
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )),
        ]
        for test_name, arrangement, expectation in test_cases:
            for path_suffix_is_required in [False, True]:
                with self.subTest(msg=test_name + ' / path_suffix_is_required = ' + str(path_suffix_is_required)):
                    self._check2(arrangement.for_path_suffix_required(path_suffix_is_required),
                                 expectation)

    def test_no_explicit_relativity(self):
        symbol = StringConstantSymbolContext('THE_SYMBOL', 'symbol-string-value')
        symbol_1 = StringConstantSymbolContext('SYMBOL_NAME_1', 'symbol-1-value')
        symbol_2 = StringConstantSymbolContext('SYMBOL_NAME_2', 'symbol-2-value')
        accepted_relativities = PathRelativityVariants({RelOptionType.REL_HDS_CASE,
                                                        RelOptionType.REL_TMP},
                                                       True)
        arg_config_for_rel_symbol_config(accepted_relativities)
        path_rel_home = path_ddvs.of_rel_option(RelOptionType.REL_HDS_CASE,
                                                path_ddvs.constant_path_part('file-in-home-dir'))
        test_cases = [
            ('Symbol reference as only argument'
             ' SHOULD '
             'be path with default relativity and suffix as string reference'
             ' GIVEN '
             'referenced symbol is a string',
             ArrangementWoSuffixRequirement(
                 source='{symbol_reference}'.format(
                     symbol_reference=symbol.name__sym_ref_syntax),
                 rel_option_argument_configuration=arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                    RelOptionType.REL_ACT),
             ),
             expect(
                 resolved_path=
                 path_ddvs.of_rel_option(RelOptionType.REL_ACT,
                                         path_ddvs.constant_path_part(symbol.str_value)),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     asrt_sym_ref.matches_reference_2(
                         symbol.name,
                         asrt_w_str_rend_rest.equals__w_str_rendering(
                             path_or_string_reference_restrictions(accepted_relativities))
                     ),
                 ]),
                 symbol_table=
                 symbol.symbol_table,
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )
             ),
            ('Symbol reference as only argument'
             ' SHOULD '
             'be an absolute path'
             ' GIVEN '
             'referenced symbol is a string that is an absolute path',
             ArrangementWoSuffixRequirement(
                 source='{symbol_reference}'.format(
                     symbol_reference=symbol_reference_syntax_for_name(symbol.name)),
                 rel_option_argument_configuration=arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                    RelOptionType.REL_ACT),
             ),
             expect(
                 resolved_path=
                 path_ddvs.absolute_file_name('/absolute/path'),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     asrt_sym_ref.matches_reference_2(
                         symbol.name,
                         asrt_w_str_rend_rest.equals__w_str_rendering(
                             path_or_string_reference_restrictions(accepted_relativities))
                     ),
                 ]),
                 symbol_table=
                 StringConstantSymbolContext(symbol.name, '/absolute/path').symbol_table,
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )
             ),
            ('Symbol reference followed by / and constant suffix'
             ' SHOULD '
             'be an absolute path'
             ' GIVEN '
             'referenced symbol is a string that is an absolute path',
             ArrangementWoSuffixRequirement(
                 source='{symbol_reference}/constant-suffix'.format(
                     symbol_reference=symbol_reference_syntax_for_name(symbol.name)),
                 rel_option_argument_configuration=arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                    RelOptionType.REL_ACT),
             ),
             expect(
                 resolved_path=
                 path_ddvs.absolute_file_name('/absolute/path/constant-suffix'),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     asrt_sym_ref.matches_reference_2(
                         symbol.name,
                         asrt_w_str_rend_rest.equals__w_str_rendering(
                             path_or_string_reference_restrictions(accepted_relativities))
                     ),
                 ]),
                 symbol_table=
                 StringConstantSymbolContext(symbol.name, '/absolute/path').symbol_table,
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )
             ),
            ('Symbol reference followed by / and symbol ref'
             ' SHOULD '
             'be an absolute path'
             ' GIVEN '
             'referenced symbol is a string that is an absolute path',
             ArrangementWoSuffixRequirement(
                 source='{symbol_reference1}/{symbol_reference2}-constant-suffix'.format(
                     symbol_reference1=symbol_reference_syntax_for_name(symbol_1.name),
                     symbol_reference2=symbol_reference_syntax_for_name(symbol_2.name),
                 ),
                 rel_option_argument_configuration=arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                    RelOptionType.REL_ACT),
             ),
             expect(
                 resolved_path=
                 path_ddvs.absolute_file_name('/absolute/path/{symbol_2_value}-constant-suffix'.format(
                     symbol_2_value=symbol_2.str_value
                 )),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     asrt_sym_ref.matches_reference_2(
                         symbol_1.name,
                         asrt_w_str_rend_rest.equals__w_str_rendering(
                             path_or_string_reference_restrictions(accepted_relativities))
                     ),
                     is_reference_to_string__w_all_indirect_refs_are_strings(symbol_2.name),
                 ]),
                 symbol_table=
                 SymbolContext.symbol_table_of_contexts([
                     StringConstantSymbolContext(symbol_1.name, '/absolute/path'),
                     symbol_2,
                 ]),
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )
             ),
            ('Symbol reference that is a string (which is not an absolute path), '
             'followed by / and multiple symbol references'
             ' SHOULD '
             'be a path that is relative the default relativity'
             ' GIVEN '
             'first referenced symbol is a string that is not an absolute path',
             ArrangementWoSuffixRequirement(
                 source='{symbol_reference}/{symbol_reference1}.{symbol_reference2}'.format(
                     symbol_reference=symbol_reference_syntax_for_name(symbol.name),
                     symbol_reference1=symbol_reference_syntax_for_name(symbol_1.name),
                     symbol_reference2=symbol_reference_syntax_for_name(symbol_2.name),
                 ),
                 rel_option_argument_configuration=arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                    RelOptionType.REL_ACT),
             ),
             expect(
                 resolved_path=
                 path_ddvs.of_rel_option(RelOptionType.REL_ACT,
                                         path_ddvs.constant_path_part('non-abs-str/non-abs-str1.non-abs-str2')),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     asrt_sym_ref.matches_reference_2(
                         symbol.name,
                         asrt_w_str_rend_rest.equals__w_str_rendering(
                             path_or_string_reference_restrictions(accepted_relativities))
                     ),
                     is_reference_to_string__w_all_indirect_refs_are_strings(symbol_1.name),
                     is_reference_to_string__w_all_indirect_refs_are_strings(symbol_2.name),
                 ]),
                 symbol_table=
                 SymbolContext.symbol_table_of_contexts([
                     StringConstantSymbolContext(symbol.name, 'non-abs-str'),
                     StringConstantSymbolContext(symbol_1.name, 'non-abs-str1'),
                     StringConstantSymbolContext(symbol_2.name, 'non-abs-str2'),
                 ]),
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )
             ),
            ('Symbol reference as only argument'
             ' SHOULD '
             'be path identical to referenced symbol'
             ' GIVEN '
             'referenced symbol is a path',
             ArrangementWoSuffixRequirement(
                 source='{symbol_reference}'.format(
                     symbol_reference=symbol_reference_syntax_for_name(symbol.name)),
                 rel_option_argument_configuration=arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                    RelOptionType.REL_ACT),
             ),
             expect(
                 resolved_path=
                 path_rel_home,
                 expected_symbol_references=
                 asrt.matches_sequence([
                     asrt_sym_ref.matches_reference_2(
                         symbol.name,
                         asrt_w_str_rend_rest.equals__w_str_rendering(
                             path_or_string_reference_restrictions(accepted_relativities))
                     ),
                 ]),
                 symbol_table=
                 PathDdvSymbolContext(symbol.name, path_rel_home).symbol_table,
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )
             ),
            ('Symbol reference as first argument, followed by / and symbol reference'
             ' SHOULD '
             'be path identical to first referenced symbol followed by / and second symbol reference'
             ' GIVEN '
             'first symbol is a path',
             ArrangementWoSuffixRequirement(
                 source='{path_symbol_reference}/{string_symbol_reference}'.format(
                     path_symbol_reference=symbol_reference_syntax_for_name(symbol_1.name),
                     string_symbol_reference=symbol_reference_syntax_for_name(symbol_2.name),
                 ),
                 rel_option_argument_configuration=arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                    RelOptionType.REL_TMP),
             ),
             expect(
                 resolved_path=
                 path_ddvs.of_rel_option(RelOptionType.REL_HDS_CASE,
                                         path_ddvs.constant_path_part('suffix-from-path-symbol/string-symbol-value')),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     asrt_sym_ref.matches_reference_2(
                         symbol_1.name,
                         asrt_w_str_rend_rest.equals__w_str_rendering(
                             path_or_string_reference_restrictions(accepted_relativities))
                     ),
                     is_reference_to_string__w_all_indirect_refs_are_strings(symbol_2.name),
                 ]),
                 symbol_table=
                 SymbolContext.symbol_table_of_contexts([
                     ConstantSuffixPathDdvSymbolContext(symbol_1.name,
                                                        RelOptionType.REL_HDS_CASE,
                                                        'suffix-from-path-symbol'),
                     StringConstantSymbolContext(symbol_2.name, 'string-symbol-value'),
                 ]),
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )),
        ]
        for test_name, arrangement, expectation in test_cases:
            assert isinstance(arrangement, ArrangementWoSuffixRequirement)
            for path_suffix_is_required in [False, True]:
                with self.subTest(msg=test_name + '/path_suffix_is_required=' + str(path_suffix_is_required)):
                    self._check2(arrangement.for_path_suffix_required(path_suffix_is_required),
                                 expectation)


class TestParseWithMandatoryPathSuffix(TestParsesBase):
    def test_fail_WHEN_missing_arguments(self):
        path_suffix_is_required = True
        arg_config = RelOptionArgumentConfiguration(
            RelOptionsConfiguration(
                PathRelativityVariants({RelOptionType.REL_HDS_CASE,
                                        RelOptionType.REL_ACT},
                                       True),
                RelOptionType.REL_HDS_CASE),
            'argument_syntax_name',
            path_suffix_is_required)
        source_cases = [
            NameAndValue(
                'empty',
                value='',
            ),
            NameAndValue(
                'just relativity option',
                value=option_string_for(REL_HDS_CASE_OPTION_NAME),
            ),
        ]
        for case in source_cases:
            with self.subTest(case.name):
                token_stream = TokenStream(case.value)
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_path(token_stream, arg_config)

    def test_relativity_and_suffix_argument_on_following_line(self):
        path_suffix_is_required = True
        default_relativity = RelOptionType.REL_HDS_CASE
        arg_config = RelOptionArgumentConfiguration(
            RelOptionsConfiguration(
                PathRelativityVariants({default_relativity,
                                        RelOptionType.REL_ACT},
                                       True),
                default_relativity),
            'argument_syntax_name',
            path_suffix_is_required)

        option_str = option_string_for(REL_HDS_CASE_OPTION_NAME)
        source_variants = [
            SourceCase('just suffix str',
                       source='\n{suffix}',
                       source_assertion=assert_token_stream(is_null=asrt.is_true)),
            SourceCase('relativity option and suffix on following line',
                       source='   \n{option_str} {suffix}',
                       source_assertion=assert_token_stream(is_null=asrt.is_true)),
            SourceCase('relativity option and suffix on separate lines',
                       source='   \n{option_str}\n {suffix}',
                       source_assertion=assert_token_stream(is_null=asrt.is_true)),
        ]
        suffix = 'suffix'
        expected_path = path_ddvs.of_rel_option(default_relativity, path_ddvs.constant_path_part(suffix))
        sdv_assertion = matches_path_sdv(expected_path,
                                         asrt.matches_sequence([]),
                                         empty_symbol_table())
        for source_case in source_variants:
            with self.subTest(name=source_case.name,
                              source=source_case.source):
                self._check2(
                    Arrangement(
                        source=source_case.source.format(option_str=option_str,
                                                         suffix=suffix),
                        rel_option_argument_configuration=arg_config
                    ),
                    Expectation2(
                        path_sdv=sdv_assertion,
                        token_stream=source_case.source_assertion,
                    )
                )


class TestParseWithOptionalPathSuffix(TestParsesBase):
    def test_no_argument_at_all(self):
        path_suffix_is_required = False
        default_and_accepted_options_variants = [
            (RelOptionType.REL_HDS_CASE,
             {RelOptionType.REL_HDS_CASE, RelOptionType.REL_ACT}),
            (RelOptionType.REL_RESULT,
             {RelOptionType.REL_RESULT, RelOptionType.REL_TMP}),
        ]
        source_cases = [
            SourceCase(
                'empty',
                source='',
                source_assertion=assert_token_stream(is_null=asrt.is_true)
            ),
            SourceCase(
                'current line is empty, following line is not',
                source='\nnext line',
                source_assertion=assert_token_stream(remaining_source=asrt.equals('\nnext line'))
            ),
        ]
        for default_option, accepted_options in default_and_accepted_options_variants:
            expected_path = path_ddvs.of_rel_option(default_option, path_ddvs.empty_path_part())
            expected_path_value = path_sdvs.constant(expected_path)
            arg_config = RelOptionArgumentConfiguration(
                RelOptionsConfiguration(
                    PathRelativityVariants(accepted_options, True),
                    default_option),
                'argument_syntax_name',
                path_suffix_is_required)
            for source_case in source_cases:
                with self.subTest(path_suffix_is_required=path_suffix_is_required,
                                  default_option=default_option):
                    self._check(
                        Arrangement(source_case.source,
                                    arg_config),
                        Expectation(expected_path_value,
                                    token_stream=source_case.source_assertion)
                    )

    def test_only_relativity_argument(self):
        used_and_default_and_accepted_options_variants = [
            (
                RelOptionType.REL_ACT,
                RelOptionType.REL_HDS_CASE,
                {RelOptionType.REL_HDS_CASE, RelOptionType.REL_ACT}
            ),
            (
                RelOptionType.REL_HDS_CASE,
                RelOptionType.REL_ACT,
                {RelOptionType.REL_HDS_CASE, RelOptionType.REL_ACT}),
        ]

        for used_option, default_option, accepted_options in used_and_default_and_accepted_options_variants:
            option_str = option_string_for(REL_OPTIONS_MAP[used_option]._option_name)
            arg_config = RelOptionArgumentConfiguration(
                RelOptionsConfiguration(
                    PathRelativityVariants(accepted_options, True),
                    default_option),
                'argument_syntax_name',
                False)
            source_variants = [
                SourceCase('just option str',
                           source='{option_str}',
                           source_assertion=assert_token_stream(is_null=asrt.is_true)),
                SourceCase('options str preceded by space',
                           source='   {option_str}',
                           source_assertion=assert_token_stream(is_null=asrt.is_true)),
                SourceCase('option str followed by space',
                           source='{option_str}   ',
                           source_assertion=assert_token_stream(is_null=asrt.is_true)),
                SourceCase('option str on first line, other text on following line',
                           source='{option_str}   \nfollowing',
                           source_assertion=assert_token_stream(remaining_source=asrt.equals('  \nfollowing'))),
            ]
            expected_path = path_ddvs.of_rel_option(used_option, path_ddvs.empty_path_part())
            sdv_assertion = matches_path_sdv(expected_path,
                                             asrt.matches_sequence([]),
                                             empty_symbol_table())
            for source_case in source_variants:
                with self.subTest(name=source_case.name,
                                  source=source_case.source):
                    self._check2(
                        Arrangement(
                            source=source_case.source.format(option_str=option_str),
                            rel_option_argument_configuration=arg_config
                        ),
                        Expectation2(
                            path_sdv=sdv_assertion,
                            token_stream=source_case.source_assertion,
                        )
                    )

    def test_relativity_and_suffix_argument(self):
        used_and_default_and_accepted_options_variants = [
            (
                RelOptionType.REL_ACT,
                RelOptionType.REL_HDS_CASE,
                {RelOptionType.REL_HDS_CASE, RelOptionType.REL_ACT}
            ),
            (
                RelOptionType.REL_HDS_CASE,
                RelOptionType.REL_ACT,
                {RelOptionType.REL_HDS_CASE, RelOptionType.REL_ACT}),
        ]

        for used_option, default_option, accepted_options in used_and_default_and_accepted_options_variants:
            option_str = option_string_for(REL_OPTIONS_MAP[used_option]._option_name)
            arg_config = RelOptionArgumentConfiguration(
                RelOptionsConfiguration(
                    PathRelativityVariants(accepted_options, True),
                    default_option),
                'argument_syntax_name',
                False)
            source_variants = [
                SourceCase('just arguments str',
                           source='{option_str} {suffix}',
                           source_assertion=assert_token_stream(is_null=asrt.is_true)),
                SourceCase('arguments preceded by space',
                           source='   {option_str} {suffix}',
                           source_assertion=assert_token_stream(is_null=asrt.is_true)),
                SourceCase('arguments followed by space',
                           source='{option_str}  {suffix}  ',
                           source_assertion=assert_token_stream(is_null=asrt.is_true)),
                SourceCase('arguments on first line, followed by non-arguments on second line',
                           source='{option_str}  {suffix}\nfollowing',
                           source_assertion=assert_token_stream(remaining_source=asrt.equals('\nfollowing'))),
            ]
            suffix = 'suffix'
            expected_path = path_ddvs.of_rel_option(used_option, path_ddvs.constant_path_part(suffix))
            sdv_assertion = matches_path_sdv(expected_path,
                                             asrt.matches_sequence([]),
                                             empty_symbol_table())
            for source_case in source_variants:
                with self.subTest(name=source_case.name,
                                  source=source_case.source):
                    self._check2(
                        Arrangement(
                            source=source_case.source.format(option_str=option_str,
                                                             suffix=suffix),
                            rel_option_argument_configuration=arg_config
                        ),
                        Expectation2(
                            path_sdv=sdv_assertion,
                            token_stream=source_case.source_assertion,
                        )
                    )


class TestParseFromParseSource(unittest.TestCase):
    def test_raise_exception_for_invalid_argument_syntax_when_invalid_quoting_of_first_token(self):
        parser = sut.PathParser(path_relativities.all_rel_options_arg_config('ARG-SYNTAX-NAME', True))
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.parse(remaining_source('"abc'))

    def test_fail_when_no_arguments_and_path_suffix_is_required(self):
        parser = sut.PathParser(path_relativities.all_rel_options_arg_config('ARG-SYNTAX-NAME', True))
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.parse(remaining_source(''))

    def test_parse_without_option(self):
        for path_suffix_is_required in [False, True]:
            parser = sut.PathParser(
                path_relativities.all_rel_options_arg_config('ARG-SYNTAX-NAME',
                                                             path_suffix_is_required)
            )
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                path = parser.parse(remaining_source('FILENAME arg2'))
                symbols = empty_symbol_table()
                actual_path_suffix = path.resolve(symbols).path_suffix()
                equals_path_part_string('FILENAME').apply_with_message(self,
                                                                       actual_path_suffix,
                                                                       'path/path_suffix')
                assert_source(remaining_part_of_current_line=asrt.equals(' arg2'))

    def test_parse_with_option(self):
        for path_suffix_is_required in [False, True]:
            parser = sut.PathParser(
                path_relativities.all_rel_options_arg_config('ARG-SYNTAX-NAME',
                                                             path_suffix_is_required)
            )

            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                path = parser.parse(
                    remaining_source(REL_CWD_OPTION + ' FILENAME arg3 arg4'),
                )
                symbols = empty_symbol_table()
                actual_path_suffix = path.resolve(symbols).path_suffix()
                equals_path_part_string('FILENAME').apply_with_message(self,
                                                                       actual_path_suffix,
                                                                       'path/path_suffix')
                assert_source(remaining_part_of_current_line=asrt.equals(' arg3 arg4'))

    def test_parse_with_initial_space(self):
        for path_suffix_is_required in [False, True]:
            parser = sut.PathParser(path_relativities.all_rel_options_arg_config('ARG-SYNTAX-NAME',
                                                                                 path_suffix_is_required))
        with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
            path = parser.parse(remaining_source('   FILENAME'))
            symbols = empty_symbol_table()
            actual_path_suffix = path.resolve(symbols).path_suffix()
            equals_path_part_string('FILENAME').apply_with_message(self,
                                                                   actual_path_suffix,
                                                                   'path/path_suffix')
            assert_source(is_at_eol=asrt.is_true)

    def test_fail_when_option_is_only_argument_and_path_suffix_is_required(self):
        parser = sut.PathParser(path_relativities.all_rel_options_arg_config('ARG-SYNTAX-NAME', True))
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.parse(remaining_source(REL_CWD_OPTION))


class TestParsesCorrectValueFromParseSource(TestParsesBase):
    def test_default_relativity_is_different_than_that_of_default_configuration(self):
        custom_configuration = RelOptionArgumentConfigurationWoSuffixRequirement(
            RelOptionsConfiguration(PathRelativityVariants({RelOptionType.REL_ACT}, True),
                                    RelOptionType.REL_ACT),
            'FILE')
        for path_suffix_is_required in [False, True]:
            parser = sut.PathParser(custom_configuration.config_for(path_suffix_is_required))
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                actual_sdv = parser.parse(remaining_source('file.txt'))
                expected_sdv = path_sdvs.constant(
                    path_ddvs.rel_act(path_ddvs.constant_path_part('file.txt')))
                assertion = equals_path_sdv(expected_sdv)
                assertion.apply_with_message(self, actual_sdv, 'path-sdv')

    def test_WHEN_an_unsupported_option_is_used_THEN_an_exception_should_be_raised(self):
        custom_configuration = RelOptionArgumentConfigurationWoSuffixRequirement(
            RelOptionsConfiguration(PathRelativityVariants({RelOptionType.REL_ACT}, True),
                                    RelOptionType.REL_ACT),
            'FILE')
        for path_suffix_is_required in [False, True]:
            parser = sut.PathParser(custom_configuration.config_for(path_suffix_is_required))
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(remaining_source('%s file.txt' % REL_TMP_OPTION))


class TestTypeMustBeEitherPathOrStringErrMsgGenerator(unittest.TestCase):
    def test_SHOULD_be_able_to_generate_an_error_message_for_every_illegal_type(self):
        symbol_value_contexts = [
            list_.ARBITRARY_SYMBOL_VALUE_CONTEXT,
            file_matcher.ARBITRARY_SYMBOL_VALUE_CONTEXT,
            st_symbol_context.ARBITRARY_SYMBOL_VALUE_CONTEXT,
            program.ARBITRARY_SYMBOL_VALUE_CONTEXT,
        ]
        for symbol_value_context in symbol_value_contexts:
            with self.subTest(invalid_type=str(symbol_value_context.value_type)):
                # ACT #
                actual = references.type_must_be_either_path_or_string__err_msg_generator(
                    'failing_symbol',
                    symbol_value_context.container,
                )
                # ASSERT #
                asrt_text_doc.assert_is_valid_text_renderer(self, actual)


def _remaining_source(ts: TokenStream) -> str:
    return ts.source[ts.position:]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
