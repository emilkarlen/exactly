import pathlib
import unittest

from exactly_lib.instructions.utils.arg_parse import parse_destination_path as sut
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.instructions.utils.arg_parse.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.instructions.utils.relativity_root import RelOptionType
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.home_and_sds import HomeAndSds
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax, short_option_syntax
from exactly_lib_test.section_document.test_resources.parse_source import assert_source
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class Configuration:
    def __init__(self,
                 default_rel_option_type: RelOptionType,
                 other_than_default_rel_option_type: RelOptionType):
        self.default_rel_option_type = default_rel_option_type
        self.other_than_default_rel_option_type = other_than_default_rel_option_type


def suite() -> unittest.TestSuite:
    configurations = [
        Configuration(rel_option_type, _other_option_type_than(rel_option_type))
        for rel_option_type in RelOptionType
        ]
    return unittest.TestSuite([_suite_for(configuration)
                               for configuration in configurations] +
                              [_suite_for_configuration_and_boolean(configuration)
                               for configuration in configurations] +
                              [_suite_for_boolean()])


def _suite_for(configuration: Configuration) -> unittest.TestSuite:
    test_cases = [
        TestDefaultRelativityOptionWithPathArgumentMandatoryWithoutArgument,
        TestDefaultRelativityOptionWithPathArgumentNOTMandatoryWithoutArgument,

    ]
    return unittest.TestSuite([tc(configuration) for tc in test_cases])


def _suite_for_configuration_and_boolean(configuration: Configuration) -> unittest.TestSuite:
    test_cases = [
        TestDefaultRelativityOptionWithSingleArgument,
        TestDefaultRelativityOptionWithMultipleArguments,

        TestNonDefaultRelativityOptionWithSingleArgument,
        TestNonDefaultRelativityOptionWithMultipleArguments,
    ]
    generated_test_cases = []
    for tc in test_cases:
        for argument_is_mandatory in [False, True]:
            generated_test_cases.append(tc(configuration, argument_is_mandatory))
    return unittest.TestSuite(generated_test_cases)


def _suite_for_boolean() -> unittest.TestSuite:
    test_cases = [
        TestParseShouldFailWhenRelativityOptionIsNotInSetOfAcceptedOptions,
    ]
    generated_test_cases = []
    for tc in test_cases:
        for argument_is_mandatory in [False, True]:
            generated_test_cases.append(tc(argument_is_mandatory))
    return unittest.TestSuite(generated_test_cases)


class Arrangement:
    def __init__(self,
                 default_type: RelOptionType,
                 path_argument_is_mandatory: bool,
                 arguments: list):
        self.arguments = ' '.join(arguments)
        self.default_rel_type = default_type
        self.path_argument_is_mandatory = path_argument_is_mandatory


class Expectation:
    def __init__(self,
                 remaining_arguments: list,
                 path_argument,
                 rel_option_type: RelOptionType):
        self.path_argument = path_argument
        self.remaining_arguments = ' '.join(remaining_arguments)
        self.rel_option_type = rel_option_type


def test(put: unittest.TestCase,
         arrangement: Arrangement,
         expectation: Expectation):
    source = remaining_source(arrangement.arguments)
    actual_path = sut.parse_destination_pathInstrDesc(
        _with_all_options_acceptable(arrangement.default_rel_type),
        arrangement.path_argument_is_mandatory,
        source)
    put.assertIs(expectation.rel_option_type,
                 actual_path.destination_type,
                 'actual destination type')
    expected_path_argument = _expected_path_argument(expectation.path_argument)
    put.assertEqual(expected_path_argument,
                    actual_path.path_argument,
                    'path argument')
    home_and_sds = _home_and_sds()
    actual_resolved_path = actual_path.resolved_path(home_and_sds)
    expected_resolved_path = _expected_resolve_path(expectation.rel_option_type,
                                                    expectation.path_argument,
                                                    home_and_sds)
    put.assertEqual(expected_resolved_path,
                    actual_resolved_path,
                    'resolved path')
    source.consume_initial_space_on_current_line()
    source_assertion = assert_source(current_line_number=asrt.equals(1),
                                     remaining_part_of_current_line=asrt.equals(expectation.remaining_arguments))
    source_assertion.apply_with_message(put, source, 'source')


def _home_and_sds() -> HomeAndSds:
    home_dir_path = pathlib.Path('home')
    sds_root_dir_name = 'sds'
    sds = SandboxDirectoryStructure(sds_root_dir_name)
    return HomeAndSds(home_dir_path, sds)


def _expected_resolve_path(rel_option_type: RelOptionType,
                           path_argument: str,
                           home_and_sds: HomeAndSds) -> pathlib.Path:
    ret_val = REL_OPTIONS_MAP[rel_option_type].root_resolver.from_home_and_sds(home_and_sds)
    if path_argument:
        ret_val /= path_argument
    return ret_val


def _expected_path_argument(path_argument: str) -> pathlib.PurePath:
    if path_argument is None:
        return pathlib.PurePath()
    else:
        return pathlib.PurePath(path_argument)


class TestCaseBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, configuration: Configuration):
        super().__init__(configuration)
        self.configuration = configuration


class TestDefaultRelativityOptionWithPathArgumentMandatoryWithoutArgument(TestCaseBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_destination_path(_with_all_options_acceptable(self.configuration.default_rel_option_type),
                                       True,
                                       [])


class TestDefaultRelativityOptionWithPathArgumentNOTMandatoryWithoutArgument(TestCaseBase):
    def runTest(self):
        test(
            self,
            Arrangement(self.configuration.default_rel_option_type,
                        False,
                        []),
            Expectation(remaining_arguments=[],
                        path_argument=None,
                        rel_option_type=self.configuration.default_rel_option_type),
        )


class TestCaseWithPathArgumentMandatoryValueBase(unittest.TestCase):
    def __init__(self, configuration: Configuration,
                 path_argument_is_mandatory: bool):
        super().__init__()
        self.configuration = configuration
        self.path_argument_is_mandatory = path_argument_is_mandatory

    def shortDescription(self):
        return '{}\n / path_argument_is_mandatory=path_argument_is_mandatory'.format(
            str(type(self.configuration)),
            self.path_argument_is_mandatory)

    def runTest(self):
        raise NotImplementedError()


class TestDefaultRelativityOptionWithSingleArgument(TestCaseWithPathArgumentMandatoryValueBase):
    def runTest(self):
        test(
            self,
            Arrangement(self.configuration.default_rel_option_type,
                        self.path_argument_is_mandatory,
                        ['arg']),
            Expectation(remaining_arguments=[],
                        path_argument='arg',
                        rel_option_type=self.configuration.default_rel_option_type),
        )


class TestDefaultRelativityOptionWithMultipleArguments(TestCaseWithPathArgumentMandatoryValueBase):
    def runTest(self):
        test(
            self,
            Arrangement(self.configuration.default_rel_option_type,
                        self.path_argument_is_mandatory,
                        ['arg1', 'arg2']),
            Expectation(remaining_arguments=['arg2'],
                        path_argument='arg1',
                        rel_option_type=self.configuration.default_rel_option_type),
        )


class TestNonDefaultRelativityOptionWithSingleArgument(TestCaseWithPathArgumentMandatoryValueBase):
    def runTest(self):
        test(
            self,
            Arrangement(self.configuration.default_rel_option_type,
                        self.path_argument_is_mandatory,
                        [arg_syntax_for(self.configuration.other_than_default_rel_option_type),
                         'arg']),
            Expectation(remaining_arguments=[],
                        path_argument='arg',
                        rel_option_type=self.configuration.other_than_default_rel_option_type),
        )


class TestNonDefaultRelativityOptionWithMultipleArguments(TestCaseWithPathArgumentMandatoryValueBase):
    def runTest(self):
        test(
            self,
            Arrangement(self.configuration.default_rel_option_type,
                        self.path_argument_is_mandatory,
                        [arg_syntax_for(self.configuration.other_than_default_rel_option_type),
                         'arg1', 'arg2']),
            Expectation(remaining_arguments=['arg2'],
                        path_argument='arg1',
                        rel_option_type=self.configuration.other_than_default_rel_option_type),
        )


class TestCaseWithBooleanBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, path_argument_is_mandatory: bool):
        super().__init__(path_argument_is_mandatory)
        self.path_argument_is_mandatory = path_argument_is_mandatory


class TestParseShouldFailWhenRelativityOptionIsNotInSetOfAcceptedOptions(TestCaseWithBooleanBase):
    def runTest(self):
        option_infos = [
            (rel_option_type, _other_option_type_than(rel_option_type))
            for rel_option_type in RelOptionType
            ]

        for accepted_type, unaccepted_type in option_infos:
            for is_rel_val_def_option_accepted in [False, True]:
                with self.subTest(accepted_type=accepted_type,
                                  unaccepted_type=unaccepted_type):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.parse_destination_path(_for(accepted_type, {accepted_type}, is_rel_val_def_option_accepted),
                                                   self.path_argument_is_mandatory,
                                                   [
                                                       arg_syntax_for(unaccepted_type),
                                                       'path-arg',
                                                   ])


def arg_syntax_for(rel_option_type: RelOptionType) -> str:
    option = REL_OPTIONS_MAP[rel_option_type].option_name
    if option.long:
        return long_option_syntax(option.long)
    else:
        return short_option_syntax(option.short)


def _other_option_type_than(option_type: RelOptionType) -> RelOptionType:
    if option_type is RelOptionType.REL_ACT:
        return RelOptionType.REL_TMP
    else:
        return RelOptionType.REL_ACT


def _with_all_options_acceptable(default: RelOptionType) -> RelOptionArgumentConfiguration:
    return _for(default, RelOptionType, True)


def _for(default: RelOptionType,
         acceptable_options: iter,
         is_rel_val_def_option_accepted: bool) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(RelOptionsConfiguration(acceptable_options,
                                                                  is_rel_val_def_option_accepted,
                                                                  default),
                                          'SYNTAX_ELEMENT')
