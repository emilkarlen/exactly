import unittest
from pathlib import Path

from exactly_lib.help_texts.file_ref import REL_SYMBOL_OPTION_NAME, REL_TMP_OPTION, REL_CWD_OPTION, \
    REL_HOME_CASE_OPTION_NAME
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.symbol.data import file_ref_resolvers2, path_part_resolvers
from exactly_lib.symbol.data import string_resolvers
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect, \
    OrReferenceRestrictions, OrRestrictionPart
from exactly_lib.symbol.data.restrictions.value_restrictions import StringRestriction, \
    FileRefRelativityRestriction
from exactly_lib.symbol.resolver_structure import SymbolContainer
from exactly_lib.symbol.restriction import ReferenceRestrictions, DataTypeReferenceRestrictions
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.test_case_utils.parse import parse_file_ref as sut
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsFixedPath, PathPartAsNothing
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.list_value import ListValue
from exactly_lib.type_system.value_type import DataValueType
from exactly_lib.util.cli_syntax.elements import argument
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.parse.token import HARD_QUOTE_CHAR, SOFT_QUOTE_CHAR
from exactly_lib.util.symbol_table import empty_symbol_table, SymbolTable
from exactly_lib_test.section_document.element_parsers.test_resources.token_stream_assertions import \
    assert_token_stream, \
    assert_token_string_is
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.data.test_resources.concrete_value_assertions import equals_file_ref_resolver, \
    matches_file_ref_resolver
from exactly_lib_test.symbol.data.test_resources.data_symbol_utils import \
    symbol_table_with_single_string_value, symbol_table_with_single_file_ref_value, symbol_table_with_string_values, \
    entry
from exactly_lib_test.symbol.data.test_resources.list_values import ListResolverTestImplForConstantListValue
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import \
    equals_symbol_reference
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.file_matcher import FileMatcherResolverConstantTestImpl
from exactly_lib_test.symbol.test_resources.lines_transformer import LinesTransformerResolverConstantTestImpl
from exactly_lib_test.test_case_utils.parse.test_resources.source_case import SourceCase
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.data.test_resources.file_matcher import FileMatcherThatSelectsAllFilesTestImpl
from exactly_lib_test.type_system.data.test_resources.path_part_assertions import equals_path_part_string
from exactly_lib_test.type_system.logic.test_resources.values import FakeLinesTransformer
from exactly_lib_test.util.test_resources.symbol_tables import symbol_table_from_entries


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
                 token_stream: asrt.ValueAssertion,
                 symbol_table_in_with_all_ref_restrictions_are_satisfied: SymbolTable = None):
        self.file_ref_resolver = file_ref_resolver
        self.token_stream = token_stream
        self.symbol_table_in_with_all_ref_restrictions_are_satisfied = symbol_table_in_with_all_ref_restrictions_are_satisfied


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


ARBITRARY_REL_OPT_ARG_CONF = RelOptionArgumentConfigurationWoSuffixRequirement(
    RelOptionsConfiguration(
        PathRelativityVariants({RelOptionType.REL_ACT}, True),
        RelOptionType.REL_ACT),
    'argument_syntax_name')


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
        ts = TokenStream(arrangement.source)
        # ACT #
        actual = sut.parse_file_ref(ts,
                                    arrangement.rel_option_argument_configuration)
        # ASSERT #
        equals_file_ref_resolver(expectation.file_ref_resolver).apply_with_message(self, actual,
                                                                                   'file-ref-resolver')
        expectation.token_stream.apply_with_message(self, ts, 'token-stream')

    def _check2(self,
                arrangement: Arrangement,
                expectation: Expectation2):
        # ARRANGE #
        ts = TokenStream(arrangement.source)
        # ACT #
        actual = sut.parse_file_ref(ts,
                                    arrangement.rel_option_argument_configuration)
        # ASSERT #
        self.__assertions_on_reference_restrictions(actual,
                                                    expectation.symbol_table_in_with_all_ref_restrictions_are_satisfied)
        expectation.file_ref_resolver.apply_with_message(self, actual, 'file-ref-resolver')
        expectation.token_stream.apply_with_message(self, ts, 'token-stream')
        self.__assertions_on_hypothetical_reference_to_resolver(
            actual,
            expectation.symbol_table_in_with_all_ref_restrictions_are_satisfied)

    def _assert_raises_invalid_argument_exception(self,
                                                  source_string: str,
                                                  test_name: str = ''):
        for path_suffix_is_required in [False, True]:
            with self.subTest(test_name=test_name,
                              path_suffix_is_required=path_suffix_is_required):
                token_stream = TokenStream(source_string)
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    rel_opt_arg_conf = ARBITRARY_REL_OPT_ARG_CONF.config_for(path_suffix_is_required)
                    sut.parse_file_ref(token_stream, rel_opt_arg_conf)

    def __assertions_on_reference_restrictions(self,
                                               actual: FileRefResolver,
                                               symbols: SymbolTable):
        for idx, reference in enumerate(actual.references):
            assert isinstance(reference, SymbolReference)  # Type info for IDE
            container = symbols.lookup(reference.name)
            assert isinstance(container, SymbolContainer)
            result = reference.restrictions.is_satisfied_by(symbols,
                                                            reference.name,
                                                            container)
            self.assertIsNone(result,
                              'Restriction on reference #{}: expects None=satisfaction'.format(idx))

    def __assertions_on_hypothetical_reference_to_resolver(
            self,
            actual: FileRefResolver,
            symbols: SymbolTable):
        restriction = FileRefRelativityRestriction(PathRelativityVariants(RelOptionType, True))
        container = data_symbol_utils.file_ref_resolver_container(actual)
        result = restriction.is_satisfied_by(symbols, 'hypothetical_symbol', container)
        self.assertIsNone(result,
                          'Result of hypothetical restriction on path')


class TestFailingParseDueToInvalidSyntax(TestParsesBase):
    def test_fail_due_to_invalid_quoting(self):
        rel_symbol_option = _option_string_for(REL_SYMBOL_OPTION_NAME)
        cases = [
            '{rel_symbol_option} SYMBOL_NAME {soft_quote}file_name'.format(rel_symbol_option=rel_symbol_option,
                                                                           soft_quote=SOFT_QUOTE_CHAR),
            '{rel_symbol_option} SYMBOL_NAME file_name{hard_quote}'.format(rel_symbol_option=rel_symbol_option,
                                                                           hard_quote=HARD_QUOTE_CHAR),
        ]
        for source_string in cases:
            self._assert_raises_invalid_argument_exception(source_string,
                                                           test_name=source_string)


class TestParseWithoutRelSymbolRelativity(TestParsesBase):
    def test_fail_when_no_arguments(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref(TokenStream(''),
                               _ARG_CONFIG_FOR_ALL_RELATIVITIES.config_for(True))

    def test_WHEN_no_relativity_option_is_given_THEN_default_relativity_SHOULD_be_used(self):
        file_name_argument = 'file-name'
        default_and_accepted_options_variants = [
            (RelOptionType.REL_HOME_CASE,
             {RelOptionType.REL_HOME_CASE, RelOptionType.REL_ACT}),
            (RelOptionType.REL_RESULT,
             {RelOptionType.REL_RESULT, RelOptionType.REL_TMP}),
        ]
        for default_option, accepted_options in default_and_accepted_options_variants:
            expected_file_ref = file_refs.of_rel_option(default_option, PathPartAsFixedPath(file_name_argument))
            expected_file_ref_value = file_ref_resolvers2.constant(expected_file_ref)
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
                            Expectation(expected_file_ref_value,
                                        token_stream_assertion)
                        )

    def test_parse_with_relativity_option_and_relative_path_suffix(self):
        file_name_argument = 'file-name'
        for rel_option_type, rel_option_info in REL_OPTIONS_MAP.items():
            expected_file_ref = file_refs.of_rel_option(rel_option_type, PathPartAsFixedPath(file_name_argument))
            expected_file_ref_resolver = file_ref_resolvers2.constant(expected_file_ref)
            option_str = _option_string_for(rel_option_info.option_name)
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
                                        _ARG_CONFIG_FOR_ALL_RELATIVITIES.config_for(path_suffix_is_required)),
                            Expectation(expected_file_ref_resolver,
                                        token_stream_assertion))

    def test_parse_with_relativity_option_and_absolute_path_suffix(self):
        file_name_argument = '/an/absolute/path'
        for rel_option_type, rel_option_info in REL_OPTIONS_MAP.items():
            expected_file_ref = file_refs.absolute_file_name(file_name_argument)
            expected_file_ref_resolver = file_ref_resolvers2.constant(expected_file_ref)
            option_str = _option_string_for(rel_option_info.option_name)
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
                                        _ARG_CONFIG_FOR_ALL_RELATIVITIES.config_for(path_suffix_is_required)),
                            Expectation(expected_file_ref_resolver,
                                        token_stream_assertion))

    def test_parse_with_only_absolute_path_suffix(self):
        file_name_argument = '/an/absolute/path'
        expected_file_ref = file_refs.absolute_file_name(file_name_argument)
        expected_file_ref_resolver = file_ref_resolvers2.constant(expected_file_ref)
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
                                    _ARG_CONFIG_FOR_ALL_RELATIVITIES.config_for(path_suffix_is_required)),
                        Expectation(expected_file_ref_resolver,
                                    token_stream_assertion))

    def test_WHEN_relativity_option_is_not_one_of_accepted_options_THEN_parse_SHOULD_fail(self):
        file_name_argument = 'file-name'
        used_and_default_and_accepted_options_variants = [
            (
                RelOptionType.REL_ACT,
                RelOptionType.REL_HOME_CASE,
                {RelOptionType.REL_HOME_CASE}
            ),
            (
                RelOptionType.REL_HOME_CASE,
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
                            sut.parse_file_ref(token_stream, arg_config)

    def test_parse_with_option_fails_when_no_file_argument(self):
        for rel_option_info in REL_OPTIONS_MAP.values():
            with self.subTest(msg=rel_option_info.informative_name):
                option_str = _option_string_for(rel_option_info.option_name)
                ts = TokenStream(option_str)
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_file_ref(ts, _ARG_CONFIG_FOR_ALL_RELATIVITIES.config_for(True))


class TestParseWithRelSymbolRelativity(TestParsesBase):
    def test_WHEN_symbol_name_is_invalid_THEN_parse_SHOULD_fail(self):
        rel_symbol_option = _option_string_for(REL_SYMBOL_OPTION_NAME)
        cases = [
            '{rel_symbol_option} INVALID_SYMBOL_NAME? file_name'.format(rel_symbol_option=rel_symbol_option),
            '{rel_symbol_option} ?INVALID_SYMBOL_NAME file_name'.format(rel_symbol_option=rel_symbol_option),
            '{rel_symbol_option} --invalid_symbol_name file_name'.format(rel_symbol_option=rel_symbol_option),
            '{rel_symbol_option} {soft_quote}invalid_symbol_name{soft_quote} file_name'.format(
                rel_symbol_option=rel_symbol_option,
                soft_quote=SOFT_QUOTE_CHAR),
            '{rel_symbol_option} ?? file_name'.format(rel_symbol_option=rel_symbol_option),
        ]
        for source_string in cases:
            self._assert_raises_invalid_argument_exception(source_string,
                                                           test_name=source_string)

    def test_WHEN_rel_symbol_option_is_quoted_THEN_parse_SHOULD_treat_that_string_as_file_name(self):
        rel_symbol_option = _option_string_for(REL_SYMBOL_OPTION_NAME)
        source = '"{rel_symbol_option}" SYMBOL_NAME file_name'.format(rel_symbol_option=rel_symbol_option)
        expected_file_ref = file_refs.of_rel_option(_ARG_CONFIG_FOR_ALL_RELATIVITIES.options.default_option,
                                                    PathPartAsFixedPath('{rel_symbol_option}'.format(
                                                        rel_symbol_option=rel_symbol_option)))
        expected_file_ref_value = file_ref_resolvers2.constant(expected_file_ref)
        for path_suffix_is_required in [False, True]:
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                self._check(
                    Arrangement(source,
                                sut.all_rel_options_config('ARG-SYNTAX-NAME', path_suffix_is_required)),
                    Expectation(expected_file_ref_value,
                                assert_token_stream(head_token=assert_token_string_is('SYMBOL_NAME')))
                )

    def test_WHEN_no_file_name_argument_is_given_and_path_suffix_is_required_THEN_parse_SHOULD_fail(self):
        rel_symbol_option = _option_string_for(REL_SYMBOL_OPTION_NAME)
        source = '{rel_symbol_option} SYMBOL_NAME'.format(rel_symbol_option=rel_symbol_option)
        token_stream = TokenStream(source)
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref(token_stream,
                               sut.all_rel_options_config('ARG-SYNTAX-NAME', True))

    def test_WHEN_no_file_name_argument_is_given_and_path_suffix_is_not_required_THEN_parse_SHOULD_succeed(self):
        rel_symbol_option = _option_string_for(REL_SYMBOL_OPTION_NAME)
        source = '{rel_symbol_option} SYMBOL_NAME'.format(rel_symbol_option=rel_symbol_option)
        token_stream = TokenStream(source)
        sut.parse_file_ref(token_stream,
                           sut.all_rel_options_config('ARG-SYNTAX-NAME', False))

    def test_reference_restrictions_on_symbol_references_in_path_suffix_SHOULD_be_string_restrictions(self):
        rel_symbol_option = _option_string_for(REL_SYMBOL_OPTION_NAME)
        accepted_relativities = PathRelativityVariants({RelOptionType.REL_HOME_CASE,
                                                        RelOptionType.REL_TMP},
                                                       True)
        relativity_of_defined_path_symbol = RelOptionType.REL_TMP
        defined_path_symbol = NameAndValue('DEFINED_PATH_SYMBOL', 'DEFINED_PATH_SYMBOL_VALUE')
        relativity_file_ref = file_refs.of_rel_option(relativity_of_defined_path_symbol,
                                                      PathPartAsFixedPath(defined_path_symbol.value))

        suffix_symbol = NameAndValue('PATH_SUFFIX_SYMBOL', 'symbol-string-value')
        suffix_string_constant = ' string constant'
        test_cases = [
            ('Symbol reference in path suffix '
             'SHOULD '
             'become a symbol reference that must be a string',
             ArrangementWoSuffixRequirement(
                 source='{rel_symbol_option} {defined_path_symbol} {suffix_symbol_reference}'.format(
                     rel_symbol_option=rel_symbol_option,
                     defined_path_symbol=defined_path_symbol.name,
                     suffix_symbol_reference=symbol_reference_syntax_for_name(suffix_symbol.name)),
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                     RelOptionType.REL_HOME_CASE),
             ),
             expect(
                 resolved_file_ref=
                 file_refs.of_rel_option(
                     relativity_of_defined_path_symbol,
                     PathPartAsFixedPath(str(Path(defined_path_symbol.value) / Path(suffix_symbol.value)))),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     equals_symbol_reference(
                         SymbolReference(defined_path_symbol.name,
                                         file_ref_reference_restrictions(accepted_relativities))),
                     equals_symbol_reference(
                         SymbolReference(suffix_symbol.name,
                                         path_part_string_reference_restrictions())),
                 ]),
                 symbol_table=
                 symbol_table_from_entries([
                     entry(defined_path_symbol.name, file_ref_resolvers2.constant(relativity_file_ref)),
                     entry(suffix_symbol.name, string_resolvers.str_constant(suffix_symbol.value)),
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
                     suffix_symbol_reference=symbol_reference_syntax_for_name(suffix_symbol.name),
                     suffix_string_constant=suffix_string_constant),
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                     RelOptionType.REL_HOME_CASE),
             ),
             expect(
                 resolved_file_ref=
                 file_refs.of_rel_option(
                     relativity_of_defined_path_symbol,
                     PathPartAsFixedPath(
                         str(Path(defined_path_symbol.value) / Path(suffix_symbol.value + suffix_string_constant)))),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     equals_symbol_reference(
                         SymbolReference(defined_path_symbol.name,
                                         file_ref_reference_restrictions(accepted_relativities))),
                     equals_symbol_reference(
                         SymbolReference(suffix_symbol.name,
                                         path_part_string_reference_restrictions())),
                 ]),
                 symbol_table=
                 symbol_table_from_entries([
                     entry(defined_path_symbol.name, file_ref_resolvers2.constant(relativity_file_ref)),
                     entry(suffix_symbol.name, string_resolvers.str_constant(suffix_symbol.value)),
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
        option_str = _option_string_for(REL_SYMBOL_OPTION_NAME)
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
                PathRelativityVariants({RelOptionType.REL_ACT, RelOptionType.REL_HOME_CASE}, False),
            ]
            for accepted_relativities in accepted_relativities_variants:
                expected_symbol_reference = SymbolReference(symbol_name,
                                                            ReferenceRestrictionsOnDirectAndIndirect(
                                                                FileRefRelativityRestriction(
                                                                    accepted_relativities)))
                expected_file_ref_resolver = file_ref_resolvers2.rel_symbol(expected_symbol_reference,
                                                                            path_part_resolvers.from_constant_str(
                                                                                file_name_argument))
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


class TestParseWithSymbolReferenceEmbeddedInPathArgument(TestParsesBase):
    def test_with_explicit_relativity(self):
        symbol = NameAndValue('PATH_SUFFIX_SYMBOL', 'symbol-string-value')
        symbol_1 = NameAndValue('SYMBOL_NAME_1', 'symbol 1 value')
        symbol_2 = NameAndValue('SYMBOL_NAME_2', 'symbol 2 value')
        test_cases = [
            ('Symbol reference after explicit relativity '
             'SHOULD '
             'become a symbol reference path suffix that must be a string',
             ArrangementWoSuffixRequirement(
                 source='{rel_home_case_option} {symbol_reference}'.format(
                     rel_home_case_option=_option_string_for_relativity(RelOptionType.REL_HOME_CASE),
                     symbol_reference=symbol_reference_syntax_for_name(symbol.name)),
                 rel_option_argument_configuration=_arg_config_with_all_accepted_and_default(RelOptionType.REL_ACT),
             ),
             expect(
                 resolved_file_ref=
                 file_refs.of_rel_option(RelOptionType.REL_HOME_CASE,
                                         PathPartAsFixedPath(
                                             symbol.value)),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     equals_symbol_reference(
                         SymbolReference(symbol.name,
                                         path_part_string_reference_restrictions())),
                 ]),
                 symbol_table=
                 symbol_table_with_single_string_value(symbol.name,
                                                       symbol.value),
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )
             ),
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
             expect(
                 resolved_file_ref=
                 file_refs.of_rel_option(RelOptionType.REL_TMP,
                                         PathPartAsFixedPath(
                                             symbol_1.value + '/const' + symbol_2.value)),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     equals_symbol_reference(
                         SymbolReference(symbol_1.name, path_part_string_reference_restrictions())),
                     equals_symbol_reference(
                         SymbolReference(symbol_2.name, path_part_string_reference_restrictions())),
                 ]),
                 symbol_table=
                 symbol_table_with_string_values([symbol_1, symbol_2]),
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
                     rel_tmp_option=_option_string_for_relativity(RelOptionType.REL_TMP),
                     symbol_reference1=symbol_reference_syntax_for_name(symbol_1.name),
                     symbol_reference2=symbol_reference_syntax_for_name(symbol_2.name)),
                 rel_option_argument_configuration=_arg_config_with_all_accepted_and_default(RelOptionType.REL_TMP),
             ),
             expect(
                 resolved_file_ref=
                 file_refs.of_rel_option(RelOptionType.REL_TMP,
                                         PathPartAsFixedPath(
                                             symbol_1.value + '/ const ' + symbol_2.value)),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     equals_symbol_reference(
                         SymbolReference(symbol_1.name, path_part_string_reference_restrictions())),
                     equals_symbol_reference(
                         SymbolReference(symbol_2.name, path_part_string_reference_restrictions())),
                 ]),
                 symbol_table=
                 symbol_table_with_string_values([symbol_1, symbol_2]),
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )),
            ('Hard quoted symbol reference after explicit relativity'
             ' SHOULD '
             'become a path suffix that is the literal quoted symbol reference',
             ArrangementWoSuffixRequirement(
                 source='{rel_home_case_option} {hard_quote}{symbol_reference}{hard_quote}'.format(
                     rel_home_case_option=_option_string_for_relativity(RelOptionType.REL_HOME_CASE),
                     hard_quote=HARD_QUOTE_CHAR,
                     symbol_reference=symbol_reference_syntax_for_name(symbol.name)),
                 rel_option_argument_configuration=_arg_config_with_all_accepted_and_default(RelOptionType.REL_ACT),
             ),
             expect(
                 resolved_file_ref=
                 file_refs.of_rel_option(
                     RelOptionType.REL_HOME_CASE,
                     PathPartAsFixedPath(symbol_reference_syntax_for_name(symbol.name))),
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
        symbol = NameAndValue('THE_SYMBOL', 'symbol-string-value')
        symbol_1 = NameAndValue('SYMBOL_NAME_1', 'symbol-1-value')
        symbol_2 = NameAndValue('SYMBOL_NAME_2', 'symbol-2-value')
        accepted_relativities = PathRelativityVariants({RelOptionType.REL_HOME_CASE,
                                                        RelOptionType.REL_TMP},
                                                       True)
        _arg_config_for_rel_symbol_config(accepted_relativities)
        file_ref_rel_home = file_refs.of_rel_option(RelOptionType.REL_HOME_CASE,
                                                    PathPartAsFixedPath('file-in-home-dir'))
        test_cases = [
            ('Symbol reference as only argument'
             ' SHOULD '
             'be file ref with default relativity and suffix as string reference'
             ' GIVEN '
             'referenced symbol is a string',
             ArrangementWoSuffixRequirement(
                 source='{symbol_reference}'.format(
                     symbol_reference=symbol_reference_syntax_for_name(symbol.name)),
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                     RelOptionType.REL_ACT),
             ),
             expect(
                 resolved_file_ref=
                 file_refs.of_rel_option(RelOptionType.REL_ACT,
                                         PathPartAsFixedPath(symbol.value)),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     equals_symbol_reference(
                         SymbolReference(symbol.name,
                                         file_ref_or_string_reference_restrictions(accepted_relativities))
                     )
                 ]),
                 symbol_table=
                 symbol_table_with_single_string_value(symbol.name, symbol.value),
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )
             ),
            ('Symbol reference as only argument'
             ' SHOULD '
             'be an absolute file ref'
             ' GIVEN '
             'referenced symbol is a string that is an absolute path',
             ArrangementWoSuffixRequirement(
                 source='{symbol_reference}'.format(
                     symbol_reference=symbol_reference_syntax_for_name(symbol.name)),
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                     RelOptionType.REL_ACT),
             ),
             expect(
                 resolved_file_ref=
                 file_refs.absolute_file_name('/absolute/path'),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     equals_symbol_reference(
                         SymbolReference(symbol.name,
                                         file_ref_or_string_reference_restrictions(accepted_relativities))
                     ),
                 ]),
                 symbol_table=
                 symbol_table_with_single_string_value(symbol.name, '/absolute/path'),
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )
             ),
            ('Symbol reference followed by / and constant suffix'
             ' SHOULD '
             'be an absolute file ref'
             ' GIVEN '
             'referenced symbol is a string that is an absolute path',
             ArrangementWoSuffixRequirement(
                 source='{symbol_reference}/constant-suffix'.format(
                     symbol_reference=symbol_reference_syntax_for_name(symbol.name)),
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                     RelOptionType.REL_ACT),
             ),
             expect(
                 resolved_file_ref=
                 file_refs.absolute_file_name('/absolute/path/constant-suffix'),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     equals_symbol_reference(
                         SymbolReference(symbol.name,
                                         file_ref_or_string_reference_restrictions(accepted_relativities))
                     )
                     ,
                 ]),
                 symbol_table=
                 symbol_table_with_single_string_value(symbol.name, '/absolute/path'),
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )
             ),
            ('Symbol reference followed by / and symbol ref'
             ' SHOULD '
             'be an absolute file ref'
             ' GIVEN '
             'referenced symbol is a string that is an absolute path',
             ArrangementWoSuffixRequirement(
                 source='{symbol_reference1}/{symbol_reference2}-constant-suffix'.format(
                     symbol_reference1=symbol_reference_syntax_for_name(symbol_1.name),
                     symbol_reference2=symbol_reference_syntax_for_name(symbol_2.name),
                 ),
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                     RelOptionType.REL_ACT),
             ),
             expect(
                 resolved_file_ref=
                 file_refs.absolute_file_name('/absolute/path/{symbol_2_value}-constant-suffix'.format(
                     symbol_2_value=symbol_2.value
                 )),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     equals_symbol_reference(
                         SymbolReference(symbol_1.name,
                                         file_ref_or_string_reference_restrictions(accepted_relativities))),
                     equals_symbol_reference(
                         SymbolReference(symbol_2.name,
                                         path_part_string_reference_restrictions())),
                 ]),
                 symbol_table=
                 symbol_table_with_string_values([(symbol_1.name, '/absolute/path'),
                                                  symbol_2]),
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
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                     RelOptionType.REL_ACT),
             ),
             expect(
                 resolved_file_ref=
                 file_refs.of_rel_option(RelOptionType.REL_ACT,
                                         PathPartAsFixedPath('non-abs-str/non-abs-str1.non-abs-str2')),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     equals_symbol_reference(
                         SymbolReference(symbol.name,
                                         file_ref_or_string_reference_restrictions(accepted_relativities))),
                     equals_symbol_reference(
                         SymbolReference(symbol_1.name,
                                         path_part_string_reference_restrictions())),
                     equals_symbol_reference(
                         SymbolReference(symbol_2.name,
                                         path_part_string_reference_restrictions())),
                 ]),
                 symbol_table=
                 symbol_table_with_string_values([(symbol.name, 'non-abs-str'),
                                                  (symbol_1.name, 'non-abs-str1'),
                                                  (symbol_2.name, 'non-abs-str2')]),
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )
             ),
            ('Symbol reference as only argument'
             ' SHOULD '
             'be file ref identical to referenced symbol'
             ' GIVEN '
             'referenced symbol is a file ref',
             ArrangementWoSuffixRequirement(
                 source='{symbol_reference}'.format(
                     symbol_reference=symbol_reference_syntax_for_name(symbol.name)),
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                     RelOptionType.REL_ACT),
             ),
             expect(
                 resolved_file_ref=
                 file_ref_rel_home,
                 expected_symbol_references=
                 asrt.matches_sequence([
                     equals_symbol_reference(
                         SymbolReference(symbol.name,
                                         file_ref_or_string_reference_restrictions(accepted_relativities))
                     )
                     ,
                 ]),
                 symbol_table=
                 symbol_table_with_single_file_ref_value(symbol.name,
                                                         file_ref_rel_home),
                 token_stream=
                 assert_token_stream(is_null=asrt.is_true),
             )
             ),
            ('Symbol reference as first argument, followed by / and symbol reference'
             ' SHOULD '
             'be file ref identical to first referenced symbol followed by / and second symbol reference'
             ' GIVEN '
             'first symbol is a file ref',
             ArrangementWoSuffixRequirement(
                 source='{file_ref_symbol_reference}/{string_symbol_reference}'.format(
                     file_ref_symbol_reference=symbol_reference_syntax_for_name(symbol_1.name),
                     string_symbol_reference=symbol_reference_syntax_for_name(symbol_2.name),
                 ),
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                     RelOptionType.REL_TMP),
             ),
             expect(
                 resolved_file_ref=
                 file_refs.of_rel_option(RelOptionType.REL_HOME_CASE,
                                         PathPartAsFixedPath('suffix-from-path-symbol/string-symbol-value')),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     equals_symbol_reference(
                         SymbolReference(symbol_1.name,
                                         file_ref_or_string_reference_restrictions(accepted_relativities))
                     ),
                     equals_symbol_reference(
                         SymbolReference(symbol_2.name,
                                         path_part_string_reference_restrictions())
                     ),
                 ]),
                 symbol_table=
                 symbol_table_from_entries([
                     entry(symbol_1.name,
                           file_ref_resolvers2.constant(file_refs.of_rel_option(RelOptionType.REL_HOME_CASE,
                                                                                PathPartAsFixedPath(
                                                                                    'suffix-from-path-symbol')))),
                     entry(symbol_2.name, string_resolvers.str_constant('string-symbol-value')),
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
                PathRelativityVariants({RelOptionType.REL_HOME_CASE,
                                        RelOptionType.REL_ACT},
                                       True),
                RelOptionType.REL_HOME_CASE),
            'argument_syntax_name',
            path_suffix_is_required)
        source_cases = [
            NameAndValue(
                'empty',
                value='',
            ),
            NameAndValue(
                'just relativity option',
                value=_option_string_for(REL_HOME_CASE_OPTION_NAME),
            ),
        ]
        for case in source_cases:
            with self.subTest(case.name):
                token_stream = TokenStream(case.value)
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_file_ref(token_stream, arg_config)

    def test_relativity_and_suffix_argument_on_following_line(self):
        path_suffix_is_required = True
        default_relativity = RelOptionType.REL_HOME_CASE
        arg_config = RelOptionArgumentConfiguration(
            RelOptionsConfiguration(
                PathRelativityVariants({default_relativity,
                                        RelOptionType.REL_ACT},
                                       True),
                default_relativity),
            'argument_syntax_name',
            path_suffix_is_required)

        option_str = _option_string_for(REL_HOME_CASE_OPTION_NAME)
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
        expected_file_ref = file_refs.of_rel_option(default_relativity, PathPartAsFixedPath(suffix))
        resolver_assertion = matches_file_ref_resolver(expected_file_ref,
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
                        file_ref_resolver=resolver_assertion,
                        token_stream=source_case.source_assertion,
                    )
                )


class TestParseWithOptionalPathSuffix(TestParsesBase):
    def test_no_argument_at_all(self):
        path_suffix_is_required = False
        default_and_accepted_options_variants = [
            (RelOptionType.REL_HOME_CASE,
             {RelOptionType.REL_HOME_CASE, RelOptionType.REL_ACT}),
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
            expected_file_ref = file_refs.of_rel_option(default_option, PathPartAsNothing())
            expected_file_ref_value = file_ref_resolvers2.constant(expected_file_ref)
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
                        Expectation(expected_file_ref_value,
                                    token_stream=source_case.source_assertion)
                    )

    def test_only_relativity_argument(self):
        used_and_default_and_accepted_options_variants = [
            (
                RelOptionType.REL_ACT,
                RelOptionType.REL_HOME_CASE,
                {RelOptionType.REL_HOME_CASE, RelOptionType.REL_ACT}
            ),
            (
                RelOptionType.REL_HOME_CASE,
                RelOptionType.REL_ACT,
                {RelOptionType.REL_HOME_CASE, RelOptionType.REL_ACT}),
        ]

        for used_option, default_option, accepted_options in used_and_default_and_accepted_options_variants:
            option_str = _option_string_for(REL_OPTIONS_MAP[used_option].option_name)
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
            expected_file_ref = file_refs.of_rel_option(used_option, PathPartAsNothing())
            resolver_assertion = matches_file_ref_resolver(expected_file_ref,
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
                            file_ref_resolver=resolver_assertion,
                            token_stream=source_case.source_assertion,
                        )
                    )

    def test_relativity_and_suffix_argument(self):
        used_and_default_and_accepted_options_variants = [
            (
                RelOptionType.REL_ACT,
                RelOptionType.REL_HOME_CASE,
                {RelOptionType.REL_HOME_CASE, RelOptionType.REL_ACT}
            ),
            (
                RelOptionType.REL_HOME_CASE,
                RelOptionType.REL_ACT,
                {RelOptionType.REL_HOME_CASE, RelOptionType.REL_ACT}),
        ]

        for used_option, default_option, accepted_options in used_and_default_and_accepted_options_variants:
            option_str = _option_string_for(REL_OPTIONS_MAP[used_option].option_name)
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
            expected_file_ref = file_refs.of_rel_option(used_option, PathPartAsFixedPath(suffix))
            resolver_assertion = matches_file_ref_resolver(expected_file_ref,
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
                            file_ref_resolver=resolver_assertion,
                            token_stream=source_case.source_assertion,
                        )
                    )


class TestParseFromParseSource(unittest.TestCase):
    def test_raise_exception_for_invalid_argument_syntax_when_invalid_quoting_of_first_token(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref_from_parse_source(remaining_source('"abc'),
                                                 sut.all_rel_options_config('ARG-SYNTAX-NAME', True))

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
                                    RelOptionType.REL_ACT),
            'FILE')
        for path_suffix_is_required in [False, True]:
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                actual_resolver = sut.parse_file_ref_from_parse_source(
                    remaining_source('file.txt'),
                    custom_configuration.config_for(path_suffix_is_required))
                expected_resolver = file_ref_resolvers2.constant(file_refs.rel_act(PathPartAsFixedPath('file.txt')))
                assertion = equals_file_ref_resolver(expected_resolver)
                assertion.apply_with_message(self, actual_resolver, 'file-ref-resolver')

    def test_WHEN_an_unsupported_option_is_used_THEN_an_exception_should_be_raised(self):
        custom_configuration = RelOptionArgumentConfigurationWoSuffixRequirement(
            RelOptionsConfiguration(PathRelativityVariants({RelOptionType.REL_ACT}, True),
                                    RelOptionType.REL_ACT),
            'FILE')
        for path_suffix_is_required in [False, True]:
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_file_ref_from_parse_source(remaining_source('%s file.txt' % REL_TMP_OPTION),
                                                         custom_configuration.config_for(path_suffix_is_required))


class TestTypeMustBeEitherPathOrStringErrMsgGenerator(unittest.TestCase):
    def test_SHOULD_be_able_to_generate_an_error_message_for_every_illegal_type(self):
        cases = [
            ListResolverTestImplForConstantListValue(ListValue([])),
            FileMatcherResolverConstantTestImpl(FileMatcherThatSelectsAllFilesTestImpl()),
            LinesTransformerResolverConstantTestImpl(FakeLinesTransformer(), []),
        ]
        for resolver in cases:
            with self.subTest(invalid_type=str(resolver.value_type)):
                resolver_container = symbol_utils.container(resolver)
                # ACT #
                actual = sut.type_must_be_either_path_or_string__err_msg_generator('failing_symbol',
                                                                                   resolver_container)
                # ASSERT #
                self.assertIsInstance(actual, str,
                                      'error message must be a ' + str(str))


def _remaining_source(ts: TokenStream) -> str:
    return ts.source[ts.position:]


_ARG_CONFIG_FOR_ALL_RELATIVITIES = RelOptionArgumentConfigurationWoSuffixRequirement(
    RelOptionsConfiguration(
        PathRelativityVariants(RelOptionType, True),
        RelOptionType.REL_HOME_CASE),
    'argument_syntax_name')


def _arg_config_with_all_accepted_and_default(default: RelOptionType
                                              ) -> RelOptionArgumentConfigurationWoSuffixRequirement:
    return RelOptionArgumentConfigurationWoSuffixRequirement(
        RelOptionsConfiguration(PathRelativityVariants(RelOptionType, True),
                                default),
        'argument_syntax_name')


def _arg_config_for_rel_symbol_config(relativity_variants: PathRelativityVariants,
                                      default: RelOptionType = None
                                      ) -> RelOptionArgumentConfigurationWoSuffixRequirement:
    if default is None:
        default = list(relativity_variants.rel_option_types)[0]
    return RelOptionArgumentConfigurationWoSuffixRequirement(
        RelOptionsConfiguration(relativity_variants,
                                default),
        'argument_syntax_name')


def _option_string_for(option_name: argument.OptionName) -> str:
    return long_option_syntax(option_name.long)


def _option_string_for_relativity(relativity: RelOptionType) -> str:
    return _option_string_for(REL_OPTIONS_MAP[relativity].option_name)


def path_part_string_reference_restrictions() -> ReferenceRestrictionsOnDirectAndIndirect:
    return ReferenceRestrictionsOnDirectAndIndirect(StringRestriction(),
                                                    StringRestriction())


def file_ref_reference_restrictions(accepted_relativities: PathRelativityVariants
                                    ) -> DataTypeReferenceRestrictions:
    return ReferenceRestrictionsOnDirectAndIndirect(FileRefRelativityRestriction(accepted_relativities))


def file_ref_or_string_reference_restrictions(accepted_relativities: PathRelativityVariants
                                              ) -> ReferenceRestrictions:
    return OrReferenceRestrictions([
        OrRestrictionPart(
            DataValueType.PATH,
            ReferenceRestrictionsOnDirectAndIndirect(FileRefRelativityRestriction(accepted_relativities))),
        OrRestrictionPart(
            DataValueType.STRING,
            path_part_string_reference_restrictions()),
    ])


def expect(resolved_file_ref: FileRef,
           expected_symbol_references: asrt.ValueAssertion,
           symbol_table: SymbolTable,
           token_stream: asrt.ValueAssertion,
           ) -> Expectation2:
    return Expectation2(
        file_ref_resolver=matches_file_ref_resolver(resolved_file_ref,
                                                    expected_symbol_references,
                                                    symbol_table),
        symbol_table_in_with_all_ref_restrictions_are_satisfied=symbol_table,
        token_stream=token_stream,
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
