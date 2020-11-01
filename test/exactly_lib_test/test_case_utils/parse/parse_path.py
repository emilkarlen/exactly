import unittest
from pathlib import Path, PurePosixPath
from typing import Optional

from exactly_lib.definitions.path import REL_SYMBOL_OPTION_NAME, REL_TMP_OPTION, REL_CWD_OPTION, \
    REL_HDS_CASE_OPTION_NAME
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolReference
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.tcfs.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.tcfs.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.test_case_utils.parse import parse_path as sut
from exactly_lib.test_case_utils.parse import path_relativities
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.type_val_deps.sym_ref.data.reference_restrictions import ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.type_val_deps.sym_ref.data.value_restrictions import PathRelativityRestriction
from exactly_lib.type_val_deps.types.path import path_ddvs, path_sdvs
from exactly_lib.type_val_deps.types.path import path_part_sdvs
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.util.cli_syntax.elements import argument
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import HARD_QUOTE_CHAR, SOFT_QUOTE_CHAR
from exactly_lib.util.symbol_table import empty_symbol_table, SymbolTable
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.section_document.element_parsers.test_resources.token_stream_assertions import \
    assert_token_stream, \
    assert_token_string_is
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources import format_rel_option
from exactly_lib_test.test_case_utils.parse.test_resources.source_case import SourceCase
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_deps.data.test_resources import concrete_restriction_assertion
from exactly_lib_test.type_val_deps.data.test_resources.symbol_reference_assertions import \
    is_reference_to_string_made_up_of_just_strings
from exactly_lib_test.type_val_deps.types.list_.test_resources import list_
from exactly_lib_test.type_val_deps.types.path.test_resources.path import PathDdvSymbolContext, PathSymbolValueContext, \
    ConstantSuffixPathDdvSymbolContext, path_or_string_reference_restrictions
from exactly_lib_test.type_val_deps.types.path.test_resources.path_part_assertions import equals_path_part_string
from exactly_lib_test.type_val_deps.types.path.test_resources.sdv_assertions import equals_path_sdv, matches_path_sdv
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources import symbol_context as st_symbol_context
from exactly_lib_test.type_val_deps.types.test_resources import file_matcher, program


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

    return ret_val


class Arrangement:
    def __init__(self,
                 source: str,
                 rel_option_argument_configuration: RelOptionArgumentConfiguration,
                 source_file_path: Optional[Path] = None):
        self.source = source
        self.rel_option_argument_configuration = rel_option_argument_configuration
        self.source_file_path = source_file_path


class Expectation:
    def __init__(self,
                 path_sdv: PathSdv,
                 token_stream: ValueAssertion):
        assert isinstance(path_sdv, PathSdv)
        self.path_sdv = path_sdv
        self.token_stream = token_stream


class Expectation2:
    def __init__(self,
                 path_sdv: ValueAssertion,
                 token_stream: ValueAssertion,
                 symbol_table_in_with_all_ref_restrictions_are_satisfied: SymbolTable = None):
        self.path_sdv = path_sdv
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
                 rel_option_argument_configuration: RelOptionArgumentConfigurationWoSuffixRequirement,
                 source_file_path: Optional[Path] = None):
        self.source = source
        self.rel_option_argument_configuration = rel_option_argument_configuration
        self.source_file_path = source_file_path

    def for_path_suffix_required(self, value: bool) -> Arrangement:
        return Arrangement(self.source,
                           self.rel_option_argument_configuration.config_for(value),
                           self.source_file_path)


class TestParsesBase(unittest.TestCase):
    def _check(self,
               arrangement: Arrangement,
               expectation: Expectation):
        # ARRANGE #
        ts = TokenStream(arrangement.source)
        # ACT #
        actual = sut.parse_path(ts,
                                arrangement.rel_option_argument_configuration,
                                arrangement.source_file_path)
        # ASSERT #
        equals_path_sdv(expectation.path_sdv).apply_with_message(self, actual,
                                                                 'path sdv')
        expectation.token_stream.apply_with_message(self, ts, 'token-stream')

    def _check2(self,
                arrangement: Arrangement,
                expectation: Expectation2):
        # ARRANGE #
        ts = TokenStream(arrangement.source)
        # ACT #
        actual = sut.parse_path(ts,
                                arrangement.rel_option_argument_configuration,
                                arrangement.source_file_path)
        # ASSERT #
        self.__assertions_on_reference_restrictions(actual,
                                                    expectation.symbol_table_in_with_all_ref_restrictions_are_satisfied)
        expectation.path_sdv.apply_with_message(self, actual, 'path-sdv')
        expectation.token_stream.apply_with_message(self, ts, 'token-stream')
        self.__assertions_on_hypothetical_reference_to_sdv(
            actual,
            expectation.symbol_table_in_with_all_ref_restrictions_are_satisfied)

    def _assert_raises_invalid_argument_exception(self,
                                                  source_string: str,
                                                  test_name: str = ''):
        for path_suffix_is_required in [False, True]:
            for source_file_location in [None, Path('/source/file/location')]:
                with self.subTest(test_name=test_name,
                                  path_suffix_is_required=path_suffix_is_required,
                                  source_file_location=source_file_location):
                    token_stream = TokenStream(source_string)
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        rel_opt_arg_conf = ARBITRARY_REL_OPT_ARG_CONF.config_for(path_suffix_is_required)
                        sut.parse_path(token_stream,
                                       rel_opt_arg_conf,
                                       source_file_location=source_file_location)

    def __assertions_on_reference_restrictions(self,
                                               actual: PathSdv,
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

    def __assertions_on_hypothetical_reference_to_sdv(
            self,
            actual: PathSdv,
            symbols: SymbolTable):
        restriction = PathRelativityRestriction(PathRelativityVariants(RelOptionType, True))
        container = PathSymbolValueContext.of_sdv(actual).container
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
            sut.parse_path(TokenStream(''),
                           _ARG_CONFIG_FOR_ALL_RELATIVITIES.config_for(True))

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
                            Expectation(expected_path_sdv,
                                        token_stream_assertion))

    def test_parse_with_relativity_option_and_absolute_path_suffix(self):
        file_name_argument = '/an/absolute/path'
        for rel_option_type, rel_option_info in REL_OPTIONS_MAP.items():
            expected_path = path_ddvs.absolute_file_name(file_name_argument)
            expected_path_sdv = path_sdvs.constant(expected_path)
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
                                    _ARG_CONFIG_FOR_ALL_RELATIVITIES.config_for(path_suffix_is_required)),
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
                            sut.parse_path(token_stream, arg_config)

    def test_parse_with_option_fails_when_no_file_argument(self):
        for rel_option_info in REL_OPTIONS_MAP.values():
            with self.subTest(msg=rel_option_info.informative_name):
                option_str = _option_string_for(rel_option_info.option_name)
                ts = TokenStream(option_str)
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_path(ts, _ARG_CONFIG_FOR_ALL_RELATIVITIES.config_for(True))


class TestParseWithRelSymbolRelativity(TestParsesBase):
    def test_WHEN_symbol_name_is_invalid_THEN_parse_SHOULD_fail(self):
        rel_symbol_option = _option_string_for(REL_SYMBOL_OPTION_NAME)
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
        rel_symbol_option = _option_string_for(REL_SYMBOL_OPTION_NAME)
        source = '"{rel_symbol_option}" SYMBOL_NAME file_name'.format(rel_symbol_option=rel_symbol_option)
        expected_path = path_ddvs.of_rel_option(_ARG_CONFIG_FOR_ALL_RELATIVITIES.options.default_option,
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
        rel_symbol_option = _option_string_for(REL_SYMBOL_OPTION_NAME)
        source = '{rel_symbol_option} SYMBOL_NAME'.format(rel_symbol_option=rel_symbol_option)
        token_stream = TokenStream(source)
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_path(token_stream,
                           path_relativities.all_rel_options_arg_config('ARG-SYNTAX-NAME', True))

    def test_WHEN_no_file_name_argument_is_given_and_path_suffix_is_not_required_THEN_parse_SHOULD_succeed(self):
        rel_symbol_option = _option_string_for(REL_SYMBOL_OPTION_NAME)
        source = '{rel_symbol_option} SYMBOL_NAME'.format(rel_symbol_option=rel_symbol_option)
        token_stream = TokenStream(source)
        sut.parse_path(token_stream,
                       path_relativities.all_rel_options_arg_config('ARG-SYNTAX-NAME', False))

    def test_reference_restrictions_on_symbol_references_in_path_suffix_SHOULD_be_string_restrictions(self):
        rel_symbol_option = _option_string_for(REL_SYMBOL_OPTION_NAME)
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
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(
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
                     suffix_symbol.reference_assertion__string_made_up_of_just_strings,
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
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(
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
                     suffix_symbol.reference_assertion__string_made_up_of_just_strings,
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
                PathRelativityVariants({RelOptionType.REL_ACT, RelOptionType.REL_HDS_CASE}, False),
            ]
            for accepted_relativities in accepted_relativities_variants:
                expected_symbol_reference = SymbolReference(symbol_name,
                                                            ReferenceRestrictionsOnDirectAndIndirect(
                                                                PathRelativityRestriction(
                                                                    accepted_relativities)))
                expected_path_sdv = path_sdvs.rel_symbol(expected_symbol_reference,
                                                         path_part_sdvs.from_constant_str(
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
        accepted_relativities = _arg_config_with_all_accepted_and_default(RelOptionType.REL_ACT)
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
                     symbol.reference_assertion__string_made_up_of_just_strings,
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
                     symbol.reference_assertion__string_made_up_of_just_strings,
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
                         concrete_restriction_assertion.equals_data_type_reference_restrictions(
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
                     rel_hds_case_option=_option_string_for_relativity(RelOptionType.REL_HDS_CASE),
                     symbol_reference=symbol.name__sym_ref_syntax),
                 rel_option_argument_configuration=_arg_config_with_all_accepted_and_default(RelOptionType.REL_ACT),
             ),
             expect(
                 resolved_path=
                 path_ddvs.of_rel_option(RelOptionType.REL_HDS_CASE,
                                         path_ddvs.constant_path_part(
                                             symbol.str_value)),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     symbol.reference_assertion__string_made_up_of_just_strings,
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
                     rel_tmp_option=_option_string_for_relativity(RelOptionType.REL_TMP),
                     symbol_reference1=symbol_1.name__sym_ref_syntax,
                     symbol_reference2=symbol_2.name__sym_ref_syntax),
                 rel_option_argument_configuration=_arg_config_with_all_accepted_and_default(RelOptionType.REL_TMP),
             ),
             expect(
                 resolved_path=
                 path_ddvs.of_rel_option(RelOptionType.REL_TMP,
                                         path_ddvs.constant_path_part(
                                             symbol_1.str_value + '/const' + symbol_2.str_value)),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     symbol_1.reference_assertion__string_made_up_of_just_strings,
                     symbol_2.reference_assertion__string_made_up_of_just_strings,
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
                     rel_tmp_option=_option_string_for_relativity(RelOptionType.REL_TMP),
                     symbol_reference1=symbol_1.name__sym_ref_syntax,
                     symbol_reference2=symbol_2.name__sym_ref_syntax),
                 rel_option_argument_configuration=_arg_config_with_all_accepted_and_default(RelOptionType.REL_TMP),
             ),
             expect(
                 resolved_path=
                 path_ddvs.of_rel_option(RelOptionType.REL_TMP,
                                         path_ddvs.constant_path_part(
                                             symbol_1.str_value + '/ const ' + symbol_2.str_value)),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     symbol_1.reference_assertion__string_made_up_of_just_strings,
                     symbol_2.reference_assertion__string_made_up_of_just_strings,
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
                     rel_hds_case_option=_option_string_for_relativity(RelOptionType.REL_HDS_CASE),
                     hard_quote=HARD_QUOTE_CHAR,
                     symbol_reference=symbol.name__sym_ref_syntax),
                 rel_option_argument_configuration=_arg_config_with_all_accepted_and_default(RelOptionType.REL_ACT),
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
        _arg_config_for_rel_symbol_config(accepted_relativities)
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
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(accepted_relativities,
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
                         concrete_restriction_assertion.equals_data_type_reference_restrictions(
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
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                     RelOptionType.REL_ACT),
             ),
             expect(
                 resolved_path=
                 path_ddvs.absolute_file_name('/absolute/path'),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     asrt_sym_ref.matches_reference_2(
                         symbol.name,
                         concrete_restriction_assertion.equals_data_type_reference_restrictions(
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
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                     RelOptionType.REL_ACT),
             ),
             expect(
                 resolved_path=
                 path_ddvs.absolute_file_name('/absolute/path/constant-suffix'),
                 expected_symbol_references=
                 asrt.matches_sequence([
                     asrt_sym_ref.matches_reference_2(
                         symbol.name,
                         concrete_restriction_assertion.equals_data_type_reference_restrictions(
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
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(accepted_relativities,
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
                         concrete_restriction_assertion.equals_data_type_reference_restrictions(
                             path_or_string_reference_restrictions(accepted_relativities))
                     ),
                     is_reference_to_string_made_up_of_just_strings(symbol_2.name),
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
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(accepted_relativities,
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
                         concrete_restriction_assertion.equals_data_type_reference_restrictions(
                             path_or_string_reference_restrictions(accepted_relativities))
                     ),
                     is_reference_to_string_made_up_of_just_strings(symbol_1.name),
                     is_reference_to_string_made_up_of_just_strings(symbol_2.name),
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
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(accepted_relativities,
                                                                                     RelOptionType.REL_ACT),
             ),
             expect(
                 resolved_path=
                 path_rel_home,
                 expected_symbol_references=
                 asrt.matches_sequence([
                     asrt_sym_ref.matches_reference_2(
                         symbol.name,
                         concrete_restriction_assertion.equals_data_type_reference_restrictions(
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
                 rel_option_argument_configuration=_arg_config_for_rel_symbol_config(accepted_relativities,
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
                         concrete_restriction_assertion.equals_data_type_reference_restrictions(
                             path_or_string_reference_restrictions(accepted_relativities))
                     ),
                     is_reference_to_string_made_up_of_just_strings(symbol_2.name),
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
                value=_option_string_for(REL_HDS_CASE_OPTION_NAME),
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

        option_str = _option_string_for(REL_HDS_CASE_OPTION_NAME)
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
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_path_from_parse_source(remaining_source('"abc'),
                                             path_relativities.all_rel_options_arg_config('ARG-SYNTAX-NAME', True))

    def test_fail_when_no_arguments_and_path_suffix_is_required(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_path_from_parse_source(remaining_source(''),
                                             path_relativities.all_rel_options_arg_config('ARG-SYNTAX-NAME', True))

    def test_parse_without_option(self):
        for path_suffix_is_required in [False, True]:
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                path = sut.parse_path_from_parse_source(remaining_source('FILENAME arg2'),
                                                        path_relativities.all_rel_options_arg_config('ARG-SYNTAX-NAME',
                                                                                                     path_suffix_is_required))
                symbols = empty_symbol_table()
                actual_path_suffix = path.resolve(symbols).path_suffix()
                equals_path_part_string('FILENAME').apply_with_message(self,
                                                                       actual_path_suffix,
                                                                       'path/path_suffix')
                assert_source(remaining_part_of_current_line=asrt.equals(' arg2'))

    def test_parse_with_option(self):
        for path_suffix_is_required in [False, True]:
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                path = sut.parse_path_from_parse_source(
                    remaining_source(REL_CWD_OPTION + ' FILENAME arg3 arg4'),
                    path_relativities.all_rel_options_arg_config('ARG-SYNTAX-NAME',
                                                                 path_suffix_is_required))
                symbols = empty_symbol_table()
                actual_path_suffix = path.resolve(symbols).path_suffix()
                equals_path_part_string('FILENAME').apply_with_message(self,
                                                                       actual_path_suffix,
                                                                       'path/path_suffix')
                assert_source(remaining_part_of_current_line=asrt.equals(' arg3 arg4'))

    def test_parse_with_initial_space(self):
        for path_suffix_is_required in [False, True]:
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                path = sut.parse_path_from_parse_source(
                    remaining_source('   FILENAME'),
                    path_relativities.all_rel_options_arg_config('ARG-SYNTAX-NAME',
                                                                 path_suffix_is_required))
                symbols = empty_symbol_table()
                actual_path_suffix = path.resolve(symbols).path_suffix()
                equals_path_part_string('FILENAME').apply_with_message(self,
                                                                       actual_path_suffix,
                                                                       'path/path_suffix')
                assert_source(is_at_eol=asrt.is_true)

    def test_fail_when_option_is_only_argument_and_path_suffix_is_required(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_path_from_parse_source(remaining_source(REL_CWD_OPTION),
                                             path_relativities.all_rel_options_arg_config('ARG-SYNTAX-NAME',
                                                                                          True))


class TestParsesCorrectValueFromParseSource(TestParsesBase):
    def test_default_relativity_is_different_than_that_of_default_configuration(self):
        custom_configuration = RelOptionArgumentConfigurationWoSuffixRequirement(
            RelOptionsConfiguration(PathRelativityVariants({RelOptionType.REL_ACT}, True),
                                    RelOptionType.REL_ACT),
            'FILE')
        for path_suffix_is_required in [False, True]:
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                actual_sdv = sut.parse_path_from_parse_source(
                    remaining_source('file.txt'),
                    custom_configuration.config_for(path_suffix_is_required))
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
            with self.subTest(msg='path_suffix_is_required=' + str(path_suffix_is_required)):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_path_from_parse_source(remaining_source('%s file.txt' % REL_TMP_OPTION),
                                                     custom_configuration.config_for(path_suffix_is_required))


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
                actual = sut.type_must_be_either_path_or_string__err_msg_generator('failing_symbol',
                                                                                   symbol_value_context.container)
                # ASSERT #
                asrt_text_doc.assert_is_valid_text_renderer(self, actual)


def _remaining_source(ts: TokenStream) -> str:
    return ts.source[ts.position:]


_ARG_CONFIG_FOR_ALL_RELATIVITIES = RelOptionArgumentConfigurationWoSuffixRequirement(
    RelOptionsConfiguration(
        PathRelativityVariants(RelOptionType, True),
        RelOptionType.REL_HDS_CASE),
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


def expect(resolved_path: PathDdv,
           expected_symbol_references: ValueAssertion,
           symbol_table: SymbolTable,
           token_stream: ValueAssertion,
           ) -> Expectation2:
    return Expectation2(
        path_sdv=matches_path_sdv(resolved_path,
                                  expected_symbol_references,
                                  symbol_table),
        symbol_table_in_with_all_ref_restrictions_are_satisfied=symbol_table,
        token_stream=token_stream,
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
