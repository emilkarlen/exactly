import unittest

from exactly_lib.help_texts.file_ref import REL_SYMBOL_OPTION_NAME, REL_TMP_OPTION, REL_CWD_OPTION
from exactly_lib.instructions.utils.arg_parse import parse_file_ref as sut
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.instructions.utils.arg_parse.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.symbol.concrete_restrictions import FileRefRelativityRestriction, \
    EitherStringOrFileRefRelativityRestriction, StringRestriction, ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.concrete_values import FileRefResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.symbol.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.symbol.value_resolvers.file_ref_with_symbol import rel_symbol
from exactly_lib.symbol.value_resolvers.path_part_resolvers import PathPartResolverAsFixedPath
from exactly_lib.test_case_file_structure import file_refs
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath, PathPartAsNothing
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.util.cli_syntax.elements import argument
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.parse.token import HARD_QUOTE_CHAR, SOFT_QUOTE_CHAR
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.section_document.parser_implementations.test_resources import assert_token_stream2, \
    assert_token_string_is
from exactly_lib_test.section_document.test_resources.parse_source import assert_source
from exactly_lib_test.symbol.test_resources.concrete_restriction_assertion import \
    equals_either_string_or_file_ref_relativity_restriction
from exactly_lib_test.symbol.test_resources.concrete_value_assertions import file_ref_resolver_equals, \
    equals_file_ref_resolver2
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import \
    equals_symbol_reference_with_restriction_on_direct_target, equals_symbol_reference
from exactly_lib_test.symbol.test_resources.symbol_utils import \
    symbol_table_with_single_string_value, symbol_table_with_single_file_ref_value, symbol_table_with_string_values
from exactly_lib_test.test_case_file_structure.test_resources.concrete_path_part import equals_path_part_string
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()

    ret_val.addTest(unittest.makeSuite(TestParseFromTokenStream2CasesWithoutRelSymbolRelativity))
    ret_val.addTest(unittest.makeSuite(TestParseFromTokenStream2CasesWithRelSymbolRelativity))

    ret_val.addTest(unittest.makeSuite(TestParseWithReferenceEmbeddedInPathSuffix))

    ret_val.addTest(unittest.makeSuite(TestParseWithoutRequiredPathSuffix))

    ret_val.addTest(unittest.makeSuite(TestParseFromParseSource))
    ret_val.addTest(unittest.makeSuite(TestParsesCorrectValueFromParseSource))

    return ret_val


class Arrangement:
    def __init__(self,
                 source: str,
                 rel_option_argument_configuration: RelOptionArgumentConfiguration):
        self.source = source
        self.rel_option_argument_configuration = rel_option_argument_configuration


class Expectation:
    def __init__(self,
                 file_ref_resolver: FileRefResolver,
                 token_stream: asrt.ValueAssertion):
        assert isinstance(file_ref_resolver, FileRefResolver)
        self.file_ref_resolver = file_ref_resolver
        self.token_stream = token_stream


class Expectation2:
    def __init__(self,
                 file_ref_resolver: asrt.ValueAssertion,
                 token_stream: asrt.ValueAssertion):
        self.file_ref_resolver = file_ref_resolver
        self.token_stream = token_stream


class RelOptionArgumentConfigurationWoSuffixRequirement(tuple):
    def __new__(cls,
                options_configuration: RelOptionsConfiguration,
                argument_syntax_name: str):
        return tuple.__new__(cls, (options_configuration,
                                   argument_syntax_name))

    @property
    def options(self) -> RelOptionsConfiguration:
        return self[0]

    @property
    def argument_syntax_name(self) -> str:
        return self[1]

    def config_for(self, path_suffix_is_required: bool) -> RelOptionArgumentConfiguration:
        return RelOptionArgumentConfiguration(self.options,
                                              self.argument_syntax_name,
                                              path_suffix_is_required)


class ArrangementWoSuffixRequirement:
    def __init__(self,
                 source: str,
                 rel_option_argument_configuration: RelOptionArgumentConfigurationWoSuffixRequirement):
        self.source = source
        self.rel_option_argument_configuration = rel_option_argument_configuration

    def for_path_suffix_required(self, value: bool) -> Arrangement:
        return Arrangement(self.source,
                           self.rel_option_argument_configuration.config_for(value))


class TestParsesBase(unittest.TestCase):
    def _check(self,
               arrangement: Arrangement,
               expectation: Expectation):
        # ARRANGE #
        ts = TokenStream2(arrangement.source)
        # ACT #
        actual = sut.parse_file_ref(ts,
                                    arrangement.rel_option_argument_configuration)
        # ASSERT #
        file_ref_resolver_equals(expectation.file_ref_resolver).apply_with_message(self, actual,
                                                                                   'file-ref-resolver')
        expectation.token_stream.apply_with_message(self, ts, 'token-stream')

    def _check2(self, arrangement: Arrangement,
                expectation: Expectation2):
        # ARRANGE #
        ts = TokenStream2(arrangement.source)
        # ACT #
        actual = sut.parse_file_ref(ts,
                                    arrangement.rel_option_argument_configuration)
        # ASSERT #
        expectation.file_ref_resolver.apply_with_message(self, actual, 'file-ref-resolver')
        expectation.token_stream.apply_with_message(self, ts, 'token-stream')


class TestParseFromTokenStream2CasesWithoutRelSymbolRelativity(TestParsesBase):
    def test_fail_when_no_arguments(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref(TokenStream2(''),
                               _ARG_CONFIG_FOR_ALL_RELATIVITIES.config_for(True))

    def test_WHEN_no_relativity_option_is_given_THEN_default_relativity_SHOULD_be_used(self):
        file_name_argument = 'file-name'
        default_and_accepted_options_variants = [
            (RelOptionType.REL_HOME,
             {RelOptionType.REL_HOME, RelOptionType.REL_ACT}),
            (RelOptionType.REL_RESULT,
             {RelOptionType.REL_RESULT, RelOptionType.REL_TMP}),
        ]
        for default_option, accepted_options in default_and_accepted_options_variants:
            expected_file_ref = file_refs.of_rel_option(default_option, PathPartAsFixedPath(file_name_argument))
            expected_file_ref_value = FileRefConstant(expected_file_ref)
            arg_config = RelOptionArgumentConfigurationWoSuffixRequirement(
                RelOptionsConfiguration(
                    PathRelativityVariants(accepted_options, True),
                    True,
                    default_option),
                'argument_syntax_name')
            source_and_token_stream_assertion_variants = [
                (
                    '{file_name_argument} arg3 arg4',
                    assert_token_stream2(is_null=asrt.is_false,
                                         head_token=assert_token_string_is('arg3')
                                         )
                ),
                (
                    '{file_name_argument}',
                    assert_token_stream2(is_null=asrt.is_true)
                ),
                (
                    '    {file_name_argument}',
                    assert_token_stream2(is_null=asrt.is_true)
                ),
                (
                    '{file_name_argument}\nnext line',
                    assert_token_stream2(is_null=asrt.is_false,
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
                            Expectation(expected_file_ref_value,
                                        token_stream_assertion)
                        )

    def test_parse_with_relativity_option_and_relative_path_suffix(self):
        file_name_argument = 'file-name'
        for rel_option_type, rel_option_info in REL_OPTIONS_MAP.items():
            expected_file_ref = file_refs.of_rel_option(rel_option_type, PathPartAsFixedPath(file_name_argument))
            expected_file_ref_resolver = FileRefConstant(expected_file_ref)
            option_str = _option_string_for(rel_option_info.option_name)
            source_and_token_stream_assertion_variants = [
                (
                    '{option_str} {file_name_argument} arg3 arg4',
                    assert_token_stream2(is_null=asrt.is_false,
                                         head_token=assert_token_string_is('arg3')
                                         )
                ),
                (
                    '{option_str} {file_name_argument}',
                    assert_token_stream2(is_null=asrt.is_true)
                ),
                (
                    '   {option_str}    {file_name_argument}',
                    assert_token_stream2(is_null=asrt.is_true)
                ),
                (
                    '{option_str} {file_name_argument}\nnext line',
                    assert_token_stream2(is_null=asrt.is_false,
                                         head_token=assert_token_string_is('next'))
                ),
            ]
            for source, token_stream_assertion in source_and_token_stream_assertion_variants:
                for path_suffix_is_required in [False, True]:
                    with self.subTest(msg=rel_option_info.description +
                            ' / path_suffix_is_required=' + str(path_suffix_is_required)):
                        argument_string = source.format(option_str=option_str,
                                                        file_name_argument=file_name_argument)
                        self._check(
                            Arrangement(argument_string,
                                        _ARG_CONFIG_FOR_ALL_RELATIVITIES.config_for(path_suffix_is_required)),
                            Expectation(expected_file_ref_resolver,
                                        token_stream_assertion))

    def test_parse_with_relativity_option_and_absolute_path_suffix(self):
        file_name_argument = '/an/absolute/path'
        for rel_option_type, rel_option_info in REL_OPTIONS_MAP.items():
            expected_file_ref = file_refs.absolute_file_name(file_name_argument)
            expected_file_ref_resolver = FileRefConstant(expected_file_ref)
            option_str = _option_string_for(rel_option_info.option_name)
            source_and_token_stream_assertion_variants = [
                (
                    '{option_str} {file_name_argument} arg3 arg4',
                    assert_token_stream2(is_null=asrt.is_false,
                                         head_token=assert_token_string_is('arg3')
                                         )
                ),
                (
                    '{option_str} {file_name_argument}',
                    assert_token_stream2(is_null=asrt.is_true)
                ),
                (
                    '   {option_str}    {file_name_argument}',
                    assert_token_stream2(is_null=asrt.is_true)
                ),
                (
                    '{option_str} {file_name_argument}\nnext line',
                    assert_token_stream2(is_null=asrt.is_false,
                                         head_token=assert_token_string_is('next'))
                ),
            ]
            for source, token_stream_assertion in source_and_token_stream_assertion_variants:
                for path_suffix_is_required in [False, True]:
                    with self.subTest(msg=rel_option_info.description +
                            ' / path_suffix_is_required=' + str(path_suffix_is_required)):
                        argument_string = source.format(option_str=option_str,
                                                        file_name_argument=file_name_argument)
                        self._check(
                            Arrangement(argument_string,
                                        _ARG_CONFIG_FOR_ALL_RELATIVITIES.config_for(path_suffix_is_required)),
                            Expectation(expected_file_ref_resolver,
                                        token_stream_assertion))

    def test_parse_with_only_absolute_path_suffix(self):
        file_name_argument = '/an/absolute/path'
        expected_file_ref = file_refs.absolute_file_name(file_name_argument)
        expected_file_ref_resolver = FileRefConstant(expected_file_ref)
        source_and_token_stream_assertion_variants = [
            (
                '{file_name_argument} arg3 arg4',
                assert_token_stream2(is_null=asrt.is_false,
                                     head_token=assert_token_string_is('arg3')
                                     )
            ),
            (
                '{file_name_argument}',
                assert_token_stream2(is_null=asrt.is_true)
            ),
            (
                '      {file_name_argument}',
                assert_token_stream2(is_null=asrt.is_true)
            ),
            (
                '{file_name_argument}\nnext line',
                assert_token_stream2(is_null=asrt.is_false,
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
                                    _ARG_CONFIG_FOR_ALL_RELATIVITIES.config_for(path_suffix_is_required)),
                        Expectation(expected_file_ref_resolver,
                                    token_stream_assertion))

    def test_WHEN_relativity_option_is_not_one_of_accepted_options_THEN_parse_SHOULD_fail(self):
        file_name_argument = 'file-name'
        used_and_default_and_accepted_options_variants = [
            (
                RelOptionType.REL_ACT,
                RelOptionType.REL_HOME,
                {RelOptionType.REL_HOME}
            ),
            (
                RelOptionType.REL_HOME,
                RelOptionType.REL_ACT,
                {RelOptionType.REL_TMP}
            ),
        ]

        for used_option, default_option, accepted_options in used_and_default_and_accepted_options_variants:
            for path_suffix_is_required in [False, True]:
                option_str = _option_string_for(REL_OPTIONS_MAP[used_option].option_name)
                arg_config = RelOptionArgumentConfiguration(
                    RelOptionsConfiguration(
                        PathRelativityVariants(accepted_options, True),
                        True,
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
                        token_stream = TokenStream2(argument_string)
                        with self.assertRaises(SingleInstructionInvalidArgumentException):
                            sut.parse_file_ref(token_stream, arg_config)

    def test_parse_with_option_fails_when_no_file_argument(self):
        for rel_option_info in REL_OPTIONS_MAP.values():
            with self.subTest(msg=rel_option_info.description):
                option_str = _option_string_for(rel_option_info.option_name)
                ts = TokenStream2(option_str)
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_file_ref(ts, _ARG_CONFIG_FOR_ALL_RELATIVITIES.config_for(True))


class TestParseFromTokenStream2CasesWithRelSymbolRelativity(TestParsesBase):
    def test_WHEN_rel_symbol_option_is_not_accepted_THEN_parse_SHOULD_fail(self):
        rel_symbol_option = _option_string_for(REL_SYMBOL_OPTION_NAME)
        source = '{rel_symbol_option} VARIABLE_NAME file_name'.format(rel_symbol_option=rel_symbol_option)
        token_stream = TokenStream2(source)
        arg_config = RelOptionArgumentConfigurationWoSuffixRequirement(
            RelOptionsConfiguration(
                PathRelativityVariants({RelOptionType.REL_ACT}, True),
                False,
                RelOptionType.REL_ACT),
            'argument_syntax_name')
        for path_suffix_is_required in [False, True]:
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_file_ref(token_stream,
                                       arg_config.config_for(path_suffix_is_required))

    def test_WHEN_rel_symbol_option_is_quoted_THEN_parse_SHOULD_treat_that_string_as_file_name(self):
        rel_symbol_option = _option_string_for(REL_SYMBOL_OPTION_NAME)
        source = '"{rel_symbol_option}" VARIABLE_NAME file_name'.format(rel_symbol_option=rel_symbol_option)
        expected_file_ref = file_refs.of_rel_option(_ARG_CONFIG_FOR_ALL_RELATIVITIES.options.default_option,
                                                    PathPartAsFixedPath('{rel_symbol_option}'.format(
                                                        rel_symbol_option=rel_symbol_option)))
        expected_file_ref_value = FileRefConstant(expected_file_ref)
        for path_suffix_is_required in [False, True]:
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                self._check(
                    Arrangement(source,
                                sut.all_rel_options_config('ARG-SYNTAX-NAME', path_suffix_is_required)),
                    Expectation(expected_file_ref_value,
                                assert_token_stream2(head_token=assert_token_string_is('VARIABLE_NAME')))
                )

    def test_WHEN_no_file_name_argument_is_given_and_path_suffix_is_required_THEN_parse_SHOULD_fail(self):
        rel_symbol_option = _option_string_for(REL_SYMBOL_OPTION_NAME)
        source = '{rel_symbol_option} VARIABLE_NAME'.format(rel_symbol_option=rel_symbol_option)
        token_stream = TokenStream2(source)
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref(token_stream,
                               sut.all_rel_options_config('ARG-SYNTAX-NAME', True))

    def test_WHEN_no_file_name_argument_is_given_and_path_suffix_is_not_required_THEN_parse_SHOULD_succeed(self):
        rel_symbol_option = _option_string_for(REL_SYMBOL_OPTION_NAME)
        source = '{rel_symbol_option} VARIABLE_NAME'.format(rel_symbol_option=rel_symbol_option)
        token_stream = TokenStream2(source)
        sut.parse_file_ref(token_stream,
                           sut.all_rel_options_config('ARG-SYNTAX-NAME', False))

    def test_parse_with_relativity_option(self):
        file_name_argument = 'file-name'
        symbol_name = 'symbol_NAME'
        option_str = _option_string_for(REL_SYMBOL_OPTION_NAME)
        source_and_token_stream_assertion_variants = [
            (
                '{option_str} {symbol_name} {file_name_argument} arg3 arg4',
                assert_token_stream2(is_null=asrt.is_false,
                                     head_token=assert_token_string_is('arg3')
                                     )
            ),
            (
                '{option_str} {symbol_name} {file_name_argument}',
                assert_token_stream2(is_null=asrt.is_true)
            ),
            (
                '   {option_str}   {symbol_name}  {file_name_argument}',
                assert_token_stream2(is_null=asrt.is_true)
            ),
            (
                '{option_str} {symbol_name}  {file_name_argument}\nnext line',
                assert_token_stream2(is_null=asrt.is_false,
                                     head_token=assert_token_string_is('next'))
            ),
        ]
        for source, token_stream_assertion in source_and_token_stream_assertion_variants:
            accepted_relativities_variants = [
                PathRelativityVariants({RelOptionType.REL_ACT}, True),
                PathRelativityVariants({RelOptionType.REL_ACT}, False),
                PathRelativityVariants({RelOptionType.REL_ACT, RelOptionType.REL_HOME}, False),
            ]
            for accepted_relativities in accepted_relativities_variants:
                expected_symbol_reference = SymbolReference(symbol_name,
                                                            ReferenceRestrictionsOnDirectAndIndirect(
                                                                FileRefRelativityRestriction(accepted_relativities)))
                expected_file_ref_resolver = rel_symbol(expected_symbol_reference,
                                                        PathPartResolverAsFixedPath(file_name_argument))
                for path_suffix_is_required in [False, True]:
                    arg_config = _arg_config_for_rel_symbol_config(accepted_relativities)
                    test_descr = 'path_suffix_is_required={} / source={}'.format(path_suffix_is_required,
                                                                                 repr(source))
                    with self.subTest(msg=test_descr):
                        argument_string = source.format(option_str=option_str,
                                                        symbol_name=symbol_name,
                                                        file_name_argument=file_name_argument)
                        self._check(
                            Arrangement(argument_string,
                                        arg_config.config_for(path_suffix_is_required)),
                            Expectation(expected_file_ref_resolver,
                                        token_stream_assertion)
                        )


class TestParseWithReferenceEmbeddedInPathSuffix(TestParsesBase):
    def test_with_explicit_relativity(self):
        symbol = NameAndValue('PATH_SUFFIX_SYMBOL', 'symbol-string-value')
        symbol_1 = NameAndValue('SYMBOL_NAME_1', 'symbol 1 value')
        symbol_2 = NameAndValue('SYMBOL_NAME_2', 'symbol 2 value')
        test_cases = [
            ('Symbol reference after explicit relativity '
             'SHOULD '
             'become a symbol reference path suffix that must be a string',
             ArrangementWoSuffixRequirement(
                 source='{rel_home_option} {symbol_reference}'.format(
                     rel_home_option=_option_string_for_relativity(RelOptionType.REL_HOME),
                     symbol_reference=symbol_reference_syntax_for_name(symbol.name)),
                 rel_option_argument_configuration=_arg_config_with_all_accepted_and_default(RelOptionType.REL_ACT),
             ),
             Expectation2(
                 file_ref_resolver=equals_file_ref_resolver2(
                     file_refs.of_rel_option(RelOptionType.REL_HOME,
                                             PathPartAsFixedPath(
                                                 symbol.value)),
                     asrt.matches_sequence([
                         equals_symbol_reference(
                             SymbolReference(symbol.name,
                                             path_part_string_reference_restrictions())),
                     ]),
                     symbol_table_with_single_string_value(symbol.name,
                                                           symbol.value)),
                 token_stream=assert_token_stream2(is_null=asrt.is_true),
             )),
            ('Mixed symbol references and constants as path suffix after explicit relativity '
             'SHOULD '
             'become a symbol reference path suffix that must be a strings',
             ArrangementWoSuffixRequirement(
                 source='{rel_tmp_option} {symbol_reference1}/const{symbol_reference2}'.format(
                     rel_tmp_option=_option_string_for_relativity(RelOptionType.REL_TMP),
                     symbol_reference1=symbol_reference_syntax_for_name(symbol_1.name),
                     symbol_reference2=symbol_reference_syntax_for_name(symbol_2.name)),
                 rel_option_argument_configuration=_arg_config_with_all_accepted_and_default(RelOptionType.REL_TMP),
             ),
             Expectation2(
                 file_ref_resolver=equals_file_ref_resolver2(
                     file_refs.of_rel_option(RelOptionType.REL_TMP,
                                             PathPartAsFixedPath(
                                                 symbol_1.value + '/const' + symbol_2.value)),
                     asrt.matches_sequence([
                         equals_symbol_reference(
                             SymbolReference(symbol_1.name, path_part_string_reference_restrictions())),
                         equals_symbol_reference(
                             SymbolReference(symbol_2.name, path_part_string_reference_restrictions())),
                     ]),
                     symbol_table_with_string_values([symbol_1, symbol_2])
                 ),
                 token_stream=assert_token_stream2(is_null=asrt.is_true),
             )),
            ('Mixed symbol references and constants - within soft quotes - as path suffix after explicit relativity '
             'SHOULD '
             'become a symbol reference path suffix that must be a strings',
             ArrangementWoSuffixRequirement(
                 source='{rel_tmp_option} {soft_quote}{symbol_reference1}/ const {symbol_reference2}{soft_quote}'.format(
                     soft_quote=SOFT_QUOTE_CHAR,
                     rel_tmp_option=_option_string_for_relativity(RelOptionType.REL_TMP),
                     symbol_reference1=symbol_reference_syntax_for_name(symbol_1.name),
                     symbol_reference2=symbol_reference_syntax_for_name(symbol_2.name)),
                 rel_option_argument_configuration=_arg_config_with_all_accepted_and_default(RelOptionType.REL_TMP),
             ),
             Expectation2(
                 file_ref_resolver=equals_file_ref_resolver2(
                     file_refs.of_rel_option(RelOptionType.REL_TMP,
                                             PathPartAsFixedPath(
                                                 symbol_1.value + '/ const ' + symbol_2.value)),
                     asrt.matches_sequence([
                         equals_symbol_reference(
                             SymbolReference(symbol_1.name, path_part_string_reference_restrictions())),
                         equals_symbol_reference(
                             SymbolReference(symbol_2.name, path_part_string_reference_restrictions())),
                     ]),
                     symbol_table_with_string_values([symbol_1, symbol_2])
                 ),
                 token_stream=assert_token_stream2(is_null=asrt.is_true),
             )),
            ('Hard quoted symbol reference after explicit relativity'
             ' SHOULD '
             'become a path suffix that is the literal quoted symbol reference',
             ArrangementWoSuffixRequirement(
                 source='{rel_home_option} {hard_quote}{symbol_reference}{hard_quote}'.format(
                     rel_home_option=_option_string_for_relativity(RelOptionType.REL_HOME),
                     hard_quote=HARD_QUOTE_CHAR,
                     symbol_reference=symbol_reference_syntax_for_name(symbol.name)),
                 rel_option_argument_configuration=_arg_config_with_all_accepted_and_default(RelOptionType.REL_ACT),
             ),
             Expectation2(
                 file_ref_resolver=file_ref_resolver_equals(
                     FileRefConstant(file_refs.of_rel_option(
                         RelOptionType.REL_HOME,
                         PathPartAsFixedPath(symbol_reference_syntax_for_name(symbol.name))))),
                 token_stream=assert_token_stream2(is_null=asrt.is_true),
             )),
        ]
        for test_name, arrangement, expectation in test_cases:
            for path_suffix_is_required in [False, True]:
                with self.subTest(msg=test_name + ' / path_suffix_is_required = ' + str(path_suffix_is_required)):
                    self._check2(arrangement.for_path_suffix_required(path_suffix_is_required),
                                 expectation)

    def test_no_explicit_relativity(self):
        symbol_name = 'THE_SYMBOL'
        symbol_string_value = 'symbol-string-value'
        accepted_relativities = PathRelativityVariants({RelOptionType.REL_HOME,
                                                        RelOptionType.REL_TMP},
                                                       True)
        _arg_config_for_rel_symbol_config(accepted_relativities)
        file_ref_rel_home = file_refs.of_rel_option(RelOptionType.REL_HOME,
                                                    PathPartAsFixedPath('file-in-home-dir'))
        test_cases = [
            ('Symbol reference as only argument'
             ' SHOULD '
             'be file ref with default relativity and suffix as string reference'
             ' GIVEN '
             'referenced symbol is a string',
             ArrangementWoSuffixRequirement(
                 source='{symbol_reference}'.format(
                     symbol_reference=symbol_reference_syntax_for_name(symbol_name)),
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                     RelOptionType.REL_ACT),
             ),
             Expectation2(
                 file_ref_resolver=equals_file_ref_resolver2(
                     file_refs.of_rel_option(RelOptionType.REL_ACT,
                                             PathPartAsFixedPath(symbol_string_value)),
                     asrt.matches_sequence([
                         equals_symbol_reference_with_restriction_on_direct_target(
                             symbol_name,
                             equals_either_string_or_file_ref_relativity_restriction(
                                 EitherStringOrFileRefRelativityRestriction(
                                     StringRestriction(),
                                     FileRefRelativityRestriction(accepted_relativities)
                                 )
                             )),
                     ]),
                     symbol_table_with_single_string_value(symbol_name, symbol_string_value)),
                 token_stream=assert_token_stream2(is_null=asrt.is_true),
             )),
            ('Symbol reference as only argument'
             ' SHOULD '
             'be an absolute file ref'
             ' GIVEN '
             'referenced symbol is a string that is an absolute path',
             ArrangementWoSuffixRequirement(
                 source='{symbol_reference}'.format(
                     symbol_reference=symbol_reference_syntax_for_name(symbol_name)),
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                     RelOptionType.REL_ACT),
             ),
             Expectation2(
                 file_ref_resolver=equals_file_ref_resolver2(
                     file_refs.absolute_file_name('/absolute/path'),
                     asrt.matches_sequence([
                         equals_symbol_reference_with_restriction_on_direct_target(
                             symbol_name,
                             equals_either_string_or_file_ref_relativity_restriction(
                                 EitherStringOrFileRefRelativityRestriction(
                                     StringRestriction(),
                                     FileRefRelativityRestriction(accepted_relativities)
                                 )
                             )),
                     ]),
                     symbol_table_with_single_string_value(symbol_name, '/absolute/path')),
                 token_stream=assert_token_stream2(is_null=asrt.is_true),
             )),
            ('Symbol reference as only argument'
             ' SHOULD '
             'be file ref identical to referenced symbol'
             ' GIVEN '
             'referenced symbol is a file ref',
             ArrangementWoSuffixRequirement(
                 source='{symbol_reference}'.format(
                     symbol_reference=symbol_reference_syntax_for_name(symbol_name)),
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                     RelOptionType.REL_ACT),
             ),
             Expectation2(
                 file_ref_resolver=equals_file_ref_resolver2(
                     file_ref_rel_home,
                     asrt.matches_sequence([
                         equals_symbol_reference_with_restriction_on_direct_target(
                             symbol_name,
                             equals_either_string_or_file_ref_relativity_restriction(
                                 EitherStringOrFileRefRelativityRestriction(
                                     StringRestriction(),
                                     FileRefRelativityRestriction(accepted_relativities)
                                 )
                             )),
                     ]),
                     symbol_table_with_single_file_ref_value(symbol_name,
                                                             file_ref_rel_home)),
                 token_stream=assert_token_stream2(is_null=asrt.is_true),
             )),
        ]
        for test_name, arrangement, expectation in test_cases:
            assert isinstance(arrangement, ArrangementWoSuffixRequirement)
            for path_suffix_is_required in [False, True]:
                with self.subTest(msg=test_name + '/path_suffix_is_required=' + str(path_suffix_is_required)):
                    self._check2(arrangement.for_path_suffix_required(path_suffix_is_required),
                                 expectation)


class TestParseWithoutRequiredPathSuffix(TestParsesBase):
    def test_no_argument_at_all(self):
        path_suffix_is_required = False
        default_and_accepted_options_variants = [
            (RelOptionType.REL_HOME,
             {RelOptionType.REL_HOME, RelOptionType.REL_ACT}),
            (RelOptionType.REL_RESULT,
             {RelOptionType.REL_RESULT, RelOptionType.REL_TMP}),
        ]
        for default_option, accepted_options in default_and_accepted_options_variants:
            expected_file_ref = file_refs.of_rel_option(default_option, PathPartAsNothing())
            expected_file_ref_value = FileRefConstant(expected_file_ref)
            arg_config = RelOptionArgumentConfiguration(
                RelOptionsConfiguration(
                    PathRelativityVariants(accepted_options, True),
                    True,
                    default_option),
                'argument_syntax_name',
                path_suffix_is_required)
            with self.subTest(' / path_suffix_is_required=' + str(path_suffix_is_required)):
                argument_string = ''
                self._check(
                    Arrangement(argument_string,
                                arg_config),
                    Expectation(expected_file_ref_value,
                                token_stream=assert_token_stream2(is_null=asrt.is_true))
                )

    def test_only_relativity_argument(self):
        used_and_default_and_accepted_options_variants = [
            (
                RelOptionType.REL_ACT,
                RelOptionType.REL_HOME,
                {RelOptionType.REL_HOME, RelOptionType.REL_ACT}
            ),
            (
                RelOptionType.REL_HOME,
                RelOptionType.REL_ACT,
                {RelOptionType.REL_HOME, RelOptionType.REL_ACT}),
        ]

        for used_option, default_option, accepted_options in used_and_default_and_accepted_options_variants:
            option_str = _option_string_for(REL_OPTIONS_MAP[used_option].option_name)
            arg_config = RelOptionArgumentConfiguration(
                RelOptionsConfiguration(
                    PathRelativityVariants(accepted_options, True),
                    True,
                    default_option),
                'argument_syntax_name',
                False)
            source_variants = [
                ('{option_str}',
                 assert_token_stream2(is_null=asrt.is_true)),
                ('   {option_str}',
                 assert_token_stream2(is_null=asrt.is_true)),
                ('{option_str}   ',
                 assert_token_stream2(is_null=asrt.is_true)),
            ]
            expected_file_ref = file_refs.of_rel_option(used_option, PathPartAsNothing())
            for source, token_stream_assertion in source_variants:
                with self.subTest(msg='used_option={} source={}'.format(option_str, repr(source))):
                    argument_string = source.format(option_str=option_str)
                    token_stream = TokenStream2(argument_string)
                    # ACT #
                    actual_file_ref_resolver = sut.parse_file_ref(token_stream, arg_config)
                    # ASSERT #
                    resolver_assertion = equals_file_ref_resolver2(expected_file_ref,
                                                                   asrt.matches_sequence([]),
                                                                   empty_symbol_table())
                    resolver_assertion.apply_with_message(self, actual_file_ref_resolver, 'file-ref-resolver')
                    token_stream_assertion.apply_with_message(self, token_stream, 'token stream')


class TestParseFromParseSource(unittest.TestCase):
    def test_fail_when_no_arguments_and_path_suffix_is_required(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref_from_parse_source(remaining_source(''),
                                                 sut.all_rel_options_config('ARG-SYNTAX-NAME', True))

    def test_parse_without_option(self):
        for path_suffix_is_required in [False, True]:
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                file_ref = sut.parse_file_ref_from_parse_source(remaining_source('FILENAME arg2'),
                                                                sut.all_rel_options_config('ARG-SYNTAX-NAME',
                                                                                           path_suffix_is_required))
                symbols = empty_symbol_table()
                actual_path_suffix = file_ref.resolve(symbols).path_suffix()
                equals_path_part_string('FILENAME').apply_with_message(self,
                                                                       actual_path_suffix,
                                                                       'file_reference/path_suffix')
                assert_source(remaining_part_of_current_line=asrt.equals(' arg2'))

    def test_parse_with_option(self):
        for path_suffix_is_required in [False, True]:
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                file_ref = sut.parse_file_ref_from_parse_source(
                    remaining_source(REL_CWD_OPTION + ' FILENAME arg3 arg4'),
                    sut.all_rel_options_config('ARG-SYNTAX-NAME',
                                               path_suffix_is_required))
                symbols = empty_symbol_table()
                actual_path_suffix = file_ref.resolve(symbols).path_suffix()
                equals_path_part_string('FILENAME').apply_with_message(self,
                                                                       actual_path_suffix,
                                                                       'file_reference/path_suffix')
                assert_source(remaining_part_of_current_line=asrt.equals(' arg3 arg4'))

    def test_parse_with_initial_space(self):
        for path_suffix_is_required in [False, True]:
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                file_ref = sut.parse_file_ref_from_parse_source(
                    remaining_source('   FILENAME'),
                    sut.all_rel_options_config('ARG-SYNTAX-NAME',
                                               path_suffix_is_required))
                symbols = empty_symbol_table()
                actual_path_suffix = file_ref.resolve(symbols).path_suffix()
                equals_path_part_string('FILENAME').apply_with_message(self,
                                                                       actual_path_suffix,
                                                                       'file_reference/path_suffix')
                assert_source(is_at_eol=asrt.is_true)

    def test_fail_when_option_is_only_argument_and_path_suffix_is_required(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref_from_parse_source(remaining_source(REL_CWD_OPTION),
                                                 sut.all_rel_options_config('ARG-SYNTAX-NAME',
                                                                            True))


class TestParsesCorrectValueFromParseSource(TestParsesBase):
    def test_default_relativity_is_different_than_that_of_default_configuration(self):
        custom_configuration = RelOptionArgumentConfigurationWoSuffixRequirement(
            RelOptionsConfiguration(PathRelativityVariants({RelOptionType.REL_ACT}, True),
                                    True,
                                    RelOptionType.REL_ACT),
            'FILE')
        for path_suffix_is_required in [False, True]:
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                actual_resolver = sut.parse_file_ref_from_parse_source(
                    remaining_source('file.txt'),
                    custom_configuration.config_for(path_suffix_is_required))
                expected_resolver = FileRefConstant(file_refs.rel_act(PathPartAsFixedPath('file.txt')))
                assertion = file_ref_resolver_equals(expected_resolver)
                assertion.apply_with_message(self, actual_resolver, 'file-ref-resolver')

    def test_WHEN_an_unsupported_option_is_used_THEN_an_exception_should_be_raised(self):
        custom_configuration = RelOptionArgumentConfigurationWoSuffixRequirement(
            RelOptionsConfiguration(PathRelativityVariants({RelOptionType.REL_ACT}, True),
                                    True,
                                    RelOptionType.REL_ACT),
            'FILE')
        for path_suffix_is_required in [False, True]:
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_file_ref_from_parse_source(remaining_source('%s file.txt' % REL_TMP_OPTION),
                                                         custom_configuration.config_for(path_suffix_is_required))


def _remaining_source(ts: TokenStream2) -> str:
    return ts.source[ts.position:]


_ARG_CONFIG_FOR_ALL_RELATIVITIES = RelOptionArgumentConfigurationWoSuffixRequirement(
    RelOptionsConfiguration(
        PathRelativityVariants(RelOptionType, True),
        True,
        RelOptionType.REL_HOME),
    'argument_syntax_name')


def _arg_config_with_all_accepted_and_default(default: RelOptionType
                                              ) -> RelOptionArgumentConfigurationWoSuffixRequirement:
    return RelOptionArgumentConfigurationWoSuffixRequirement(
        RelOptionsConfiguration(PathRelativityVariants(RelOptionType, True),
                                True,
                                default),
        'argument_syntax_name')


def _arg_config_for_rel_symbol_config(relativity_variants: PathRelativityVariants,
                                      default: RelOptionType = None
                                      ) -> RelOptionArgumentConfigurationWoSuffixRequirement:
    if default is None:
        default = list(relativity_variants.rel_option_types)[0]
    return RelOptionArgumentConfigurationWoSuffixRequirement(
        RelOptionsConfiguration(
            relativity_variants,
            True,
            default),
        'argument_syntax_name')


def _option_string_for(option_name: argument.OptionName) -> str:
    return long_option_syntax(option_name.long)


def _option_string_for_relativity(relativity: RelOptionType) -> str:
    return _option_string_for(REL_OPTIONS_MAP[relativity].option_name)


def path_part_string_reference_restrictions() -> ReferenceRestrictionsOnDirectAndIndirect:
    return ReferenceRestrictionsOnDirectAndIndirect(StringRestriction(),
                                                    StringRestriction())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
