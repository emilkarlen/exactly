import pathlib
import unittest

from exactly_lib.instructions.utils.arg_parse import parse_file_ref as sut
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.instructions.utils.arg_parse.symbol import symbol_reference_syntax_for_name
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.test_case_file_structure import file_refs
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath, PathPartAsNothing
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_file_structure.relative_path_options import REL_CWD_OPTION, REL_TMP_OPTION, REL_OPTIONS_MAP, \
    REL_SYMBOL_OPTION_NAME
from exactly_lib.util.cli_syntax.elements import argument
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib.value_definition.concrete_restrictions import FileRefRelativityRestriction, \
    EitherStringOrFileRefRelativityRestriction, StringRestriction
from exactly_lib.value_definition.concrete_values import FileRefResolver
from exactly_lib.value_definition.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.value_definition.value_resolvers.file_ref_with_val_def import rel_value_definition
from exactly_lib.value_definition.value_resolvers.path_part_resolvers import PathPartResolverAsFixedPath
from exactly_lib.value_definition.value_structure import ValueReference
from exactly_lib_test.section_document.parser_implementations.test_resources import assert_token_stream2, \
    assert_token_string_is
from exactly_lib_test.section_document.test_resources.parse_source import assert_source
from exactly_lib_test.test_case_file_structure.test_resources.concrete_path_part import equals_path_part_string
from exactly_lib_test.test_case_file_structure.test_resources.paths import dummy_home_and_sds
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.value_definition.test_resources.concrete_restriction_assertion import \
    equals_either_string_or_file_ref_relativity_restriction, is_string_value_restriction
from exactly_lib_test.value_definition.test_resources.concrete_value_assertions_2 import file_ref_resolver_equals, \
    equals_file_ref_resolver2
from exactly_lib_test.value_definition.test_resources.value_definition_utils import \
    symbol_table_with_single_string_value, symbol_table_with_single_file_ref_value
from exactly_lib_test.value_definition.test_resources.value_reference_assertions import equals_value_reference


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()

    ret_val.addTest(unittest.makeSuite(TestParseFromTokenStream2CasesWithoutRelValueDefinitionRelativity))
    ret_val.addTest(unittest.makeSuite(TestParseFromTokenStream2CasesWithRelValueDefinitionRelativity))

    ret_val.addTest(unittest.makeSuite(TestParseFromParseSource))
    ret_val.addTest(unittest.makeSuite(TestParsesCorrectValueFromParseSource))

    ret_val.addTest(unittest.makeSuite(TestParseWithReferenceEmbeddedInArgument))

    ret_val.addTest(unittest.makeSuite(TestParseWithoutRequiredPathSuffix))
    return ret_val


class Arrangement:
    def __init__(self,
                 source: str,
                 rel_option_argument_configuration: RelOptionArgumentConfiguration):
        self.source = source
        self.rel_option_argument_configuration = rel_option_argument_configuration


class Expectation:
    def __init__(self,
                 file_ref: FileRefResolver,
                 token_stream: asrt.ValueAssertion):
        assert isinstance(file_ref, FileRefResolver)
        self.file_ref = file_ref
        self.token_stream = token_stream


class Expectation2:
    def __init__(self,
                 file_ref: asrt.ValueAssertion,
                 token_stream: asrt.ValueAssertion):
        self.file_ref = file_ref
        self.token_stream = token_stream


class TestParsesBase(unittest.TestCase):
    def _check(self,
               arrangement: Arrangement,
               path_suffix_is_required: bool,
               expectation: Expectation):
        # ARRANGE #
        ts = TokenStream2(arrangement.source)
        # ACT #
        actual = sut.parse_file_ref(ts,
                                    arrangement.rel_option_argument_configuration,
                                    path_suffix_is_required)
        # ASSERT #
        file_ref_resolver_equals(expectation.file_ref).apply_with_message(self, actual, 'file-ref')
        expectation.token_stream.apply_with_message(self, ts, 'token-stream')

    def _check2(self, arrangement: Arrangement,
                path_suffix_is_required: bool,
                expectation: Expectation2):
        # ARRANGE #
        ts = TokenStream2(arrangement.source)
        # ACT #
        actual = sut.parse_file_ref(ts,
                                    arrangement.rel_option_argument_configuration,
                                    path_suffix_is_required)
        # ASSERT #
        expectation.file_ref.apply_with_message(self, actual, 'file-ref')
        expectation.token_stream.apply_with_message(self, ts, 'token-stream')

    # TODO remove this - replace with better test
    def assert_is_file_that_does_not_exist_pre_sds(self,
                                                   expected_path: pathlib.Path,
                                                   environment: PathResolvingEnvironmentPreOrPostSds,
                                                   actual: FileRefResolver):
        actual_file_ref = actual.resolve(environment.value_definitions)
        self.assertFalse(actual_file_ref.exists_pre_sds())
        self.assertEqual(actual_file_ref.file_path_post_sds(environment.sds),
                         expected_path)
        self.assertEqual(actual_file_ref.file_path_pre_or_post_sds(environment.home_and_sds),
                         expected_path)


class TestParseFromTokenStream2CasesWithoutRelValueDefinitionRelativity(TestParsesBase):
    def test_fail_when_no_arguments(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref(TokenStream2(''),
                               _ARG_CONFIG_FOR_ALL_RELATIVITIES,
                               True)

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
            arg_config = RelOptionArgumentConfiguration(
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
                                        arg_config),
                            path_suffix_is_required,
                            Expectation(expected_file_ref_value,
                                        token_stream_assertion)
                        )

    def test_parse_with_relativity_option(self):
        file_name_argument = 'file-name'
        for rel_option_type, rel_option_info in REL_OPTIONS_MAP.items():
            expected_file_ref = file_refs.of_rel_option(rel_option_type, PathPartAsFixedPath(file_name_argument))
            expected_file_ref_value = FileRefConstant(expected_file_ref)
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
                                        _ARG_CONFIG_FOR_ALL_RELATIVITIES),
                            path_suffix_is_required,
                            Expectation(expected_file_ref_value,
                                        token_stream_assertion)
                        )

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
                {RelOptionType.REL_TMP}),
        ]

        for used_option, default_option, accepted_options in used_and_default_and_accepted_options_variants:
            option_str = _option_string_for(REL_OPTIONS_MAP[used_option].option_name)
            arg_config = RelOptionArgumentConfiguration(
                RelOptionsConfiguration(
                    PathRelativityVariants(accepted_options, True),
                    True,
                    default_option),
                'argument_syntax_name')
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
                    sut.parse_file_ref(ts, _ARG_CONFIG_FOR_ALL_RELATIVITIES)


class TestParseFromTokenStream2CasesWithRelValueDefinitionRelativity(TestParsesBase):
    def test_WHEN_rel_val_def_option_is_not_accepted_THEN_parse_SHOULD_fail(self):
        rel_val_def_option = _option_string_for(REL_SYMBOL_OPTION_NAME)
        source = '{rel_val_def_option} VARIABLE_NAME file_name'.format(rel_val_def_option=rel_val_def_option)
        token_stream = TokenStream2(source)
        arg_config = RelOptionArgumentConfiguration(
            RelOptionsConfiguration(
                PathRelativityVariants({RelOptionType.REL_ACT}, True),
                False,
                RelOptionType.REL_ACT),
            'argument_syntax_name')
        for path_suffix_is_required in [False, True]:
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_file_ref(token_stream, arg_config, path_suffix_is_required)

    def test_WHEN_rel_val_def_option_is_quoted_THEN_parse_SHOULD_treat_that_string_as_file_name(self):
        rel_val_def_option = _option_string_for(REL_SYMBOL_OPTION_NAME)
        source = '"{rel_val_def_option}" VARIABLE_NAME file_name'.format(rel_val_def_option=rel_val_def_option)
        expected_file_ref = file_refs.of_rel_option(_ARG_CONFIG_FOR_ALL_RELATIVITIES.options.default_option,
                                                    PathPartAsFixedPath('{rel_val_def_option}'.format(
                                                        rel_val_def_option=rel_val_def_option)))
        expected_file_ref_value = FileRefConstant(expected_file_ref)
        for path_suffix_is_required in [False, True]:
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                self._check(
                    Arrangement(source,
                                _ARG_CONFIG_FOR_ALL_RELATIVITIES),
                    path_suffix_is_required,
                    Expectation(expected_file_ref_value,
                                assert_token_stream2(head_token=assert_token_string_is('VARIABLE_NAME')))
                )

    def test_WHEN_no_file_name_argument_is_given_and_path_suffix_is_required_THEN_parse_SHOULD_fail(self):
        rel_val_def_option = _option_string_for(REL_SYMBOL_OPTION_NAME)
        source = '{rel_val_def_option} VARIABLE_NAME'.format(rel_val_def_option=rel_val_def_option)
        token_stream = TokenStream2(source)
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref(token_stream, _ARG_CONFIG_FOR_ALL_RELATIVITIES, True)

    def test_WHEN_no_file_name_argument_is_given_and_path_suffix_is_not_required_THEN_parse_SHOULD_succeed(self):
        rel_val_def_option = _option_string_for(REL_SYMBOL_OPTION_NAME)
        source = '{rel_val_def_option} VARIABLE_NAME'.format(rel_val_def_option=rel_val_def_option)
        token_stream = TokenStream2(source)
        sut.parse_file_ref(token_stream, _ARG_CONFIG_FOR_ALL_RELATIVITIES, False)

    def test_parse_with_relativity_option(self):
        file_name_argument = 'file-name'
        value_definition_name = 'VALUE_DEFINITION_NAME'
        option_str = _option_string_for(REL_SYMBOL_OPTION_NAME)
        source_and_token_stream_assertion_variants = [
            (
                '{option_str} {value_definition_name} {file_name_argument} arg3 arg4',
                assert_token_stream2(is_null=asrt.is_false,
                                     head_token=assert_token_string_is('arg3')
                                     )
            ),
            (
                '{option_str} {value_definition_name} {file_name_argument}',
                assert_token_stream2(is_null=asrt.is_true)
            ),
            (
                '   {option_str}   {value_definition_name}  {file_name_argument}',
                assert_token_stream2(is_null=asrt.is_true)
            ),
            (
                '{option_str} {value_definition_name}  {file_name_argument}\nnext line',
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
                expected_value_reference = ValueReference(value_definition_name,
                                                          FileRefRelativityRestriction(accepted_relativities))
                expected_file_ref_resolver = rel_value_definition(expected_value_reference,
                                                                  PathPartResolverAsFixedPath(file_name_argument))
                arg_config = _arg_config_for_rel_val_def_config(accepted_relativities)
                for path_suffix_is_required in [False, True]:
                    test_descr = 'path_suffix_is_required={} / source={}'.format(path_suffix_is_required,
                                                                                 repr(source))
                    with self.subTest(msg=test_descr):
                        argument_string = source.format(option_str=option_str,
                                                        value_definition_name=value_definition_name,
                                                        file_name_argument=file_name_argument)
                        self._check(
                            Arrangement(argument_string,
                                        arg_config),
                            path_suffix_is_required,
                            Expectation(expected_file_ref_resolver,
                                        token_stream_assertion)
                        )


class TestParseWithReferenceEmbeddedInArgument(TestParsesBase):
    def test_with_explicit_relativity(self):
        symbol_name = 'PATH_SUFFIX_SYMBOL'
        symbol_string_value = 'symbol-string-value'
        test_cases = [
            ('Symbol reference after explicit relativity '
             'SHOULD '
             'become a symbol reference path suffix that must be a string',
             Arrangement(
                 source='{rel_home_option} {symbol_reference}'.format(
                     rel_home_option=_option_string_for_relativity(RelOptionType.REL_HOME),
                     symbol_reference=symbol_reference_syntax_for_name(symbol_name)),
                 rel_option_argument_configuration=_arg_config_with_all_accepted_and_default(RelOptionType.REL_ACT),
             ),
             Expectation2(
                 file_ref=equals_file_ref_resolver2(file_refs.of_rel_option(RelOptionType.REL_HOME,
                                                                            PathPartAsFixedPath(symbol_string_value)),
                                                    asrt.matches_sequence([
                                                        equals_value_reference(symbol_name,
                                                                               is_string_value_restriction)
                                                    ]),
                                                    symbol_table_with_single_string_value(symbol_name,
                                                                                          symbol_string_value)),
                 token_stream=assert_token_stream2(is_null=asrt.is_true),
             )),
            ('Quoted symbol reference after explicit relativity'
             ' SHOULD '
             'become a path suffix that is the literal quoted symbol reference',
             Arrangement(
                 source='{rel_home_option} \'{symbol_reference}\''.format(
                     rel_home_option=_option_string_for_relativity(RelOptionType.REL_HOME),
                     symbol_reference=symbol_reference_syntax_for_name(symbol_name)),
                 rel_option_argument_configuration=_arg_config_with_all_accepted_and_default(RelOptionType.REL_ACT),
             ),
             Expectation2(
                 file_ref=file_ref_resolver_equals(
                     FileRefConstant(file_refs.of_rel_option(
                         RelOptionType.REL_HOME,
                         PathPartAsFixedPath(symbol_reference_syntax_for_name(symbol_name))))),
                 token_stream=assert_token_stream2(is_null=asrt.is_true),
             )),
        ]
        for test_name, arrangement, expectation in test_cases:
            for path_suffix_is_required in [False, True]:
                with self.subTest(msg=test_name + ' / path_suffix_is_required = ' + str(path_suffix_is_required)):
                    self._check2(arrangement, path_suffix_is_required, expectation)

    def test_no_explicit_relativity(self):
        symbol_name = 'THE_SYMBOL'
        symbol_string_value = 'symbol-string-value'
        accepted_relativities = PathRelativityVariants({RelOptionType.REL_HOME,
                                                        RelOptionType.REL_TMP},
                                                       True)
        _arg_config_for_rel_val_def_config(accepted_relativities)
        file_ref_rel_home = file_refs.of_rel_option(RelOptionType.REL_HOME,
                                                    PathPartAsFixedPath('file-in-home-dir'))
        test_cases = [
            ('Symbol reference as only argument'
             ' SHOULD '
             'be file ref with default relativity and suffix as string reference'
             ' GIVEN '
             'referenced symbol is a string',
             Arrangement(
                 source='{symbol_reference}'.format(
                     symbol_reference=symbol_reference_syntax_for_name(symbol_name)),
                 rel_option_argument_configuration=_arg_config_for_rel_val_def_config(accepted_relativities,
                                                                                      RelOptionType.REL_ACT),
             ),
             Expectation2(
                 file_ref=equals_file_ref_resolver2(
                     file_refs.of_rel_option(RelOptionType.REL_ACT,
                                             PathPartAsFixedPath(symbol_string_value)),
                     asrt.matches_sequence([
                         equals_value_reference(
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
             Arrangement(
                 source='{symbol_reference}'.format(
                     symbol_reference=symbol_reference_syntax_for_name(symbol_name)),
                 rel_option_argument_configuration=_arg_config_for_rel_val_def_config(accepted_relativities,
                                                                                      RelOptionType.REL_ACT),
             ),
             Expectation2(
                 file_ref=equals_file_ref_resolver2(
                     file_refs.absolute_file_name('/absolute/path'),
                     asrt.matches_sequence([
                         equals_value_reference(
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
             Arrangement(
                 source='{symbol_reference}'.format(
                     symbol_reference=symbol_reference_syntax_for_name(symbol_name)),
                 rel_option_argument_configuration=_arg_config_for_rel_val_def_config(accepted_relativities,
                                                                                      RelOptionType.REL_ACT),
             ),
             Expectation2(
                 file_ref=equals_file_ref_resolver2(
                     file_ref_rel_home,
                     asrt.matches_sequence([
                         equals_value_reference(
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
            for path_suffix_is_required in [False, True]:
                with self.subTest(msg=test_name + '/path_suffix_is_required=' + str(path_suffix_is_required)):
                    self._check2(arrangement, path_suffix_is_required, expectation)


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
                'argument_syntax_name')
            with self.subTest(' / path_suffix_is_required=' + str(path_suffix_is_required)):
                argument_string = ''
                self._check(
                    Arrangement(argument_string,
                                arg_config),
                    path_suffix_is_required,
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
                'argument_syntax_name')
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
                    actual_file_ref_resolver = sut.parse_file_ref(token_stream, arg_config, False)
                    # ASSERT #
                    resolver_assertion = equals_file_ref_resolver2(expected_file_ref,
                                                                   asrt.matches_sequence([]),
                                                                   empty_symbol_table())
                    resolver_assertion.apply_with_message(self, actual_file_ref_resolver, 'file-ref-resolver')
                    token_stream_assertion.apply_with_message(self, token_stream, 'token stream')


class TestParseFromParseSource(unittest.TestCase):
    def test_fail_when_no_arguments_and_path_suffix_is_required(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref_from_parse_source(remaining_source(''), sut.ALL_REL_OPTIONS_CONFIG, True)

    def test_parse_without_option(self):
        for path_suffix_is_required in [False, True]:
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                file_ref = sut.parse_file_ref_from_parse_source(remaining_source('FILENAME arg2'),
                                                                sut.ALL_REL_OPTIONS_CONFIG,
                                                                path_suffix_is_required)
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
                    sut.ALL_REL_OPTIONS_CONFIG,
                    path_suffix_is_required)
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
                    sut.ALL_REL_OPTIONS_CONFIG,
                    path_suffix_is_required)
                symbols = empty_symbol_table()
                actual_path_suffix = file_ref.resolve(symbols).path_suffix()
                equals_path_part_string('FILENAME').apply_with_message(self,
                                                                       actual_path_suffix,
                                                                       'file_reference/path_suffix')
                assert_source(is_at_eol=asrt.is_true)

    def test_fail_when_option_is_only_argument_and_path_suffix_is_required(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref_from_parse_source(remaining_source(REL_CWD_OPTION),
                                                 sut.ALL_REL_OPTIONS_CONFIG,
                                                 True)


class TestParsesCorrectValueFromParseSource(TestParsesBase):
    def test_default_relativity_is_different_than_that_of_default_configuration(self):
        custom_configuration = RelOptionArgumentConfiguration(
            RelOptionsConfiguration(PathRelativityVariants({RelOptionType.REL_ACT}, True),
                                    True,
                                    RelOptionType.REL_ACT),
            'FILE')
        for path_suffix_is_required in [False, True]:
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                file_reference = sut.parse_file_ref_from_parse_source(remaining_source('file.txt'),
                                                                      custom_configuration,
                                                                      path_suffix_is_required)
                home_and_sds = dummy_home_and_sds()
                expected_path = home_and_sds.sds.act_dir / 'file.txt'
                environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
                self.assert_is_file_that_does_not_exist_pre_sds(expected_path,
                                                                environment,
                                                                file_reference)

    def test_WHEN_an_unsupported_option_is_used_THEN_an_exception_should_be_raised(self):
        custom_configuration = RelOptionArgumentConfiguration(
            RelOptionsConfiguration(PathRelativityVariants({RelOptionType.REL_ACT}, True),
                                    True,
                                    RelOptionType.REL_ACT),
            'FILE')
        for path_suffix_is_required in [False, True]:
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_file_ref_from_parse_source(remaining_source('%s file.txt' % REL_TMP_OPTION),
                                                         custom_configuration,
                                                         path_suffix_is_required)


def _remaining_source(ts: TokenStream2) -> str:
    return ts.source[ts.position:]


_ARG_CONFIG_FOR_ALL_RELATIVITIES = RelOptionArgumentConfiguration(
    RelOptionsConfiguration(
        PathRelativityVariants(RelOptionType, True),
        True,
        RelOptionType.REL_HOME),
    'argument_syntax_name')


def _arg_config_with_all_accepted_and_default(default: RelOptionType) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(
        RelOptionsConfiguration(PathRelativityVariants(RelOptionType, True),
                                True,
                                default),
        'argument_syntax_name')


def _arg_config_for_rel_val_def_config(relativity_variants: PathRelativityVariants,
                                       default: RelOptionType = None) -> RelOptionArgumentConfiguration:
    if default is None:
        default = list(relativity_variants.rel_option_types)[0]
    return RelOptionArgumentConfiguration(
        RelOptionsConfiguration(
            relativity_variants,
            True,
            default),
        'argument_syntax_name')


def _option_string_for(option_name: argument.OptionName) -> str:
    return long_option_syntax(option_name.long)


def _option_string_for_relativity(relativity: RelOptionType) -> str:
    return _option_string_for(REL_OPTIONS_MAP[relativity].option_name)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
