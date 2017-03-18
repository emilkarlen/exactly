import pathlib
import unittest

from exactly_lib.instructions.utils.arg_parse import parse_file_ref as sut
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.test_case_file_structure import file_refs
from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.file_ref_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_file_structure.relative_path_options import REL_CWD_OPTION, REL_TMP_OPTION, REL_OPTIONS_MAP, \
    REL_VARIABLE_DEFINITION_OPTION_NAME
from exactly_lib.util.cli_syntax.elements import argument
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.value_definition.concrete_restrictions import FileRefRelativityRestriction
from exactly_lib.value_definition.file_ref_with_val_def import rel_value_definition
from exactly_lib.value_definition.value_structure import ValueReference
from exactly_lib_test.section_document.parser_implementations.test_resources import assert_token_stream2, \
    assert_token_string_is
from exactly_lib_test.section_document.test_resources.parse_source import assert_source
from exactly_lib_test.test_case_file_structure.test_resources.file_ref import file_ref_equals
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()

    ret_val.addTest(unittest.makeSuite(TestParseFromTokenStream2CasesWithoutRelValueDefinitionRelativity))
    ret_val.addTest(unittest.makeSuite(TestParseFromTokenStream2CasesWithRelValueDefinitionRelativity))

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
                 file_ref: FileRef,
                 token_stream: asrt.ValueAssertion):
        self.file_ref = file_ref
        self.token_stream = token_stream


class TestParsesBase(unittest.TestCase):
    def _check(self, arrangement: Arrangement,
               expectation: Expectation):
        ts = TokenStream2(arrangement.source)
        actual = sut.parse_file_ref(ts, arrangement.rel_option_argument_configuration)
        file_ref_equals(expectation.file_ref).apply_with_message(self, actual, 'file-ref')
        expectation.token_stream.apply_with_message(self, ts, 'token-stream')

    def assert_is_file_that_exists_pre_sds(self,
                                           expected_path: pathlib.Path,
                                           environment: PathResolvingEnvironmentPreOrPostSds,
                                           actual: FileRef):
        self.assertTrue(actual.exists_pre_sds(environment.value_definitions))
        self.assertEqual(actual.file_path_pre_sds(environment),
                         expected_path)
        self.assertEqual(actual.file_path_pre_or_post_sds(environment),
                         expected_path)

    def assert_is_file_that_does_not_exist_pre_sds(self,
                                                   expected_path: pathlib.Path,
                                                   environment: PathResolvingEnvironmentPreOrPostSds,
                                                   actual: FileRef):
        self.assertFalse(actual.exists_pre_sds(environment.value_definitions))
        self.assertEqual(actual.file_path_post_sds(environment),
                         expected_path)
        self.assertEqual(actual.file_path_pre_or_post_sds(environment),
                         expected_path)


class TestParseFromTokenStream2CasesWithoutRelValueDefinitionRelativity(TestParsesBase):
    def test_fail_when_no_arguments(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref(TokenStream2(''),
                               _ARG_CONFIG_FOR_ALL_RELATIVITIES)

    def test_WHEN_no_relativity_option_is_given_THEN_default_relativity_SHOULD_be_used(self):
        file_name_argument = 'file-name'
        default_and_accepted_options_variants = [
            (RelOptionType.REL_HOME,
             {RelOptionType.REL_HOME, RelOptionType.REL_ACT}),
            (RelOptionType.REL_RESULT,
             {RelOptionType.REL_RESULT, RelOptionType.REL_TMP}),
        ]
        for default_option, accepted_options in default_and_accepted_options_variants:
            expected_file_ref = file_refs.of_rel_option(default_option, file_name_argument)
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
                with self.subTest(msg='source=' + repr(source)):
                    argument_string = source.format(file_name_argument=file_name_argument)
                    self._check(
                        Arrangement(argument_string,
                                    arg_config),
                        Expectation(expected_file_ref,
                                    token_stream_assertion)
                    )

    def test_parse_with_relativity_option(self):
        file_name_argument = 'file-name'
        for rel_option_type, rel_option_info in REL_OPTIONS_MAP.items():
            expected_file_ref = file_refs.of_rel_option(rel_option_type, file_name_argument)
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
                with self.subTest(msg=rel_option_info.description):
                    argument_string = source.format(option_str=option_str,
                                                    file_name_argument=file_name_argument)
                    self._check(
                        Arrangement(argument_string,
                                    _ARG_CONFIG_FOR_ALL_RELATIVITIES),
                        Expectation(expected_file_ref,
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
        rel_val_def_option = _option_string_for(REL_VARIABLE_DEFINITION_OPTION_NAME)
        source = '{rel_val_def_option} VARIABLE_NAME file_name'.format(rel_val_def_option=rel_val_def_option)
        token_stream = TokenStream2(source)
        arg_config = RelOptionArgumentConfiguration(
            RelOptionsConfiguration(
                PathRelativityVariants({RelOptionType.REL_ACT}, True),
                False,
                RelOptionType.REL_ACT),
            'argument_syntax_name')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref(token_stream, arg_config)

    def test_WHEN_rel_val_def_option_is_quoted_THEN_parse_SHOULD_treat_that_string_as_file_name(self):
        rel_val_def_option = _option_string_for(REL_VARIABLE_DEFINITION_OPTION_NAME)
        source = '"{rel_val_def_option}" VARIABLE_NAME file_name'.format(rel_val_def_option=rel_val_def_option)
        expected_file_ref = file_refs.of_rel_option(_ARG_CONFIG_FOR_ALL_RELATIVITIES.options.default_option,
                                                    '{rel_val_def_option}'.format(
                                                        rel_val_def_option=rel_val_def_option))
        self._check(
            Arrangement(source,
                        _ARG_CONFIG_FOR_ALL_RELATIVITIES),
            Expectation(expected_file_ref,
                        assert_token_stream2(head_token=assert_token_string_is('VARIABLE_NAME')))
        )

    def test_WHEN_no_file_name_argument_is_given_THEN_parse_SHOULD_fail(self):
        rel_val_def_option = _option_string_for(REL_VARIABLE_DEFINITION_OPTION_NAME)
        source = '{rel_val_def_option} VARIABLE_NAME'.format(rel_val_def_option=rel_val_def_option)
        token_stream = TokenStream2(source)
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref(token_stream, _ARG_CONFIG_FOR_ALL_RELATIVITIES)

    def test_parse_with_relativity_option(self):
        file_name_argument = 'file-name'
        value_definition_name = 'VALUE_DEFINITION_NAME'
        option_str = _option_string_for(REL_VARIABLE_DEFINITION_OPTION_NAME)
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
                expected_file_ref = rel_value_definition(expected_value_reference, file_name_argument)
                arg_config = _arg_config_for_rel_val_def_config(accepted_relativities)
                with self.subTest(msg='source={}'.format(repr(source))):
                    argument_string = source.format(option_str=option_str,
                                                    value_definition_name=value_definition_name,
                                                    file_name_argument=file_name_argument)
                    self._check(
                        Arrangement(argument_string,
                                    arg_config),
                        Expectation(expected_file_ref,
                                    token_stream_assertion)
                    )


class TestParseFromParseSource(unittest.TestCase):
    def test_fail_when_no_arguments(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref_from_parse_source(remaining_source(''), sut.ALL_REL_OPTIONS_CONFIG)

    def test_parse_without_option(self):
        file_ref = sut.parse_file_ref_from_parse_source(remaining_source('FILENAME arg2'),
                                                        sut.ALL_REL_OPTIONS_CONFIG)
        self.assertEquals('FILENAME',
                          file_ref.file_name)
        assert_source(remaining_part_of_current_line=asrt.equals(' arg2'))

    def test_parse_with_option(self):
        file_ref = sut.parse_file_ref_from_parse_source(
            remaining_source(REL_CWD_OPTION + ' FILENAME arg3 arg4'),
            sut.ALL_REL_OPTIONS_CONFIG)
        self.assertEquals('FILENAME',
                          file_ref.file_name)
        assert_source(remaining_part_of_current_line=asrt.equals(' arg3 arg4'))

    def test_parse_with_initial_space(self):
        file_ref = sut.parse_file_ref_from_parse_source(
            remaining_source('   FILENAME'),
            sut.ALL_REL_OPTIONS_CONFIG)
        self.assertEquals('FILENAME',
                          file_ref.file_name)
        assert_source(is_at_eol=asrt.is_true)

    def test_fail_when_option_is_only_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref_from_parse_source(remaining_source(REL_CWD_OPTION),
                                                 sut.ALL_REL_OPTIONS_CONFIG)


class TestParsesCorrectValueFromParseSource(TestParsesBase):
    def test_default_relativity_is_different_than_that_of_default_configuration(self):
        custom_configuration = RelOptionArgumentConfiguration(
            RelOptionsConfiguration(PathRelativityVariants({RelOptionType.REL_ACT}, True),
                                    True,
                                    RelOptionType.REL_ACT),
            'FILE')
        file_reference = sut.parse_file_ref_from_parse_source(remaining_source('file.txt'),
                                                              custom_configuration)
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
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
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_file_ref_from_parse_source(remaining_source('%s file.txt' % REL_TMP_OPTION),
                                                 custom_configuration)


def _remaining_source(ts: TokenStream2) -> str:
    return ts.source[ts.position:]


_ARG_CONFIG_FOR_ALL_RELATIVITIES = RelOptionArgumentConfiguration(
    RelOptionsConfiguration(
        PathRelativityVariants(RelOptionType, True),
        True,
        RelOptionType.REL_HOME),
    'argument_syntax_name')


def _arg_config_for_rel_val_def_config(relativity_variants: PathRelativityVariants) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(
        RelOptionsConfiguration(
            relativity_variants,
            True,
            list(relativity_variants)[0]),
        'argument_syntax_name')


def _option_string_for(option_name: argument.OptionName) -> str:
    return long_option_syntax(option_name.long)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
