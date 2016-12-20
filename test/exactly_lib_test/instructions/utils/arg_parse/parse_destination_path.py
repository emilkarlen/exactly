import pathlib
import unittest

from exactly_lib.instructions.utils.arg_parse import parse_destination_path as sut
from exactly_lib.instructions.utils.arg_parse.relative_path_options import RelOptionType, REL_OPTIONS_MAP
from exactly_lib.instructions.utils.destination_path import DestinationType
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType


class Configuration:
    def __init__(self,
                 default_type: DestinationType,
                 rel_option_type: RelOptionType):
        self.default_type = default_type
        self.rel_option_type = rel_option_type


def suite() -> unittest.TestSuite:
    configurations = [
        Configuration(DestinationType.REL_ACT_DIR, RelOptionType.REL_ACT)
    ]
    return unittest.TestSuite([suite_for(configuration)
                               for configuration in configurations] +
                              [suite_for_configuration_and_boolean(configuration)
                               for configuration in configurations])


def suite_for(configuration: Configuration) -> unittest.TestSuite:
    test_cases = [
        TestDefaultOptionWithoutArgumentButArgumentIsRequired,
        TestDefaultRelativityOptionPathArgumentNOTMandatoryWithoutArgument,
    ]
    return unittest.TestSuite([tc(configuration) for tc in test_cases])


def suite_for_configuration_and_boolean(configuration: Configuration) -> unittest.TestSuite:
    test_cases = [
        TestDefaultRelativityOptionWithSingleArgument,
        TestDefaultRelativityOptionWithMultipleArguments,
    ]
    generated_test_cases = []
    for tc in test_cases:
        for argument_is_mandatory in [False, True]:
            generated_test_cases.append(tc(configuration, argument_is_mandatory))
    return unittest.TestSuite(generated_test_cases)


class Arrangement:
    def __init__(self,
                 default_type: DestinationType,
                 path_argument_is_mandatory: bool,
                 arguments: list):
        self.arguments = arguments
        self.default_type = default_type
        self.path_argument_is_mandatory = path_argument_is_mandatory


class Expectation:
    def __init__(self,
                 relativity: DestinationType,
                 remaining_arguments: list,
                 path_argument,
                 rel_option_type: RelOptionType,
                 ):
        self.path_argument = path_argument
        self.remaining_arguments = remaining_arguments
        self.relativity = relativity
        self.rel_option_type = rel_option_type


def test(put: unittest.TestCase,
         arrangement: Arrangement,
         expectation: Expectation):
    actual_path, actual_remaining_arguments = sut.parse_destination_path(arrangement.default_type,
                                                                         arrangement.path_argument_is_mandatory,
                                                                         arrangement.arguments)
    put.assertIs(expectation.relativity,
                 actual_path.destination_type,
                 'actual destination type')
    put.assertListEqual(expectation.remaining_arguments,
                        actual_remaining_arguments,
                        'remaining arguments')
    expected_path_argument = _expected_path_argument(expectation.path_argument)
    put.assertEqual(expected_path_argument,
                    actual_path.path_argument,
                    'path argument')
    home_and_sds = _home_and_sds()
    actual_resolved_path = actual_path.resolved_path(home_and_sds.sds)
    expected_resolved_path = _expected_resolve_path(expectation.rel_option_type,
                                                    expectation.path_argument,
                                                    home_and_sds)
    put.assertEqual(expected_resolved_path,
                    actual_resolved_path,
                    'resolved path')


def _home_and_sds() -> HomeAndSds:
    home_dir_path = pathlib.Path('home')
    sds_root_dir_name = 'sds'
    sds = SandboxDirectoryStructure(sds_root_dir_name)
    return HomeAndSds(home_dir_path, sds)


def _expected_resolve_path(rel_option_type: RelOptionType,
                           path_argument: str,
                           home_and_sds: HomeAndSds) -> pathlib.Path:
    ret_val = REL_OPTIONS_MAP[rel_option_type].home_and_sds_2_path(home_and_sds)
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


class TestDefaultOptionWithoutArgumentButArgumentIsRequired(TestCaseBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_destination_path(self.configuration.default_type,
                                       True,
                                       [])


class TestDefaultRelativityOptionPathArgumentNOTMandatoryWithoutArgument(TestCaseBase):
    def runTest(self):
        test(
            self,
            Arrangement(self.configuration.default_type,
                        False,
                        []),
            Expectation(relativity=self.configuration.default_type,
                        remaining_arguments=[],
                        path_argument=None,
                        rel_option_type=self.configuration.rel_option_type),
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
            Arrangement(self.configuration.default_type,
                        self.path_argument_is_mandatory,
                        ['arg']),
            Expectation(relativity=self.configuration.default_type,
                        remaining_arguments=[],
                        path_argument='arg',
                        rel_option_type=self.configuration.rel_option_type),
        )


class TestDefaultRelativityOptionWithMultipleArguments(TestCaseWithPathArgumentMandatoryValueBase):
    def runTest(self):
        test(
            self,
            Arrangement(self.configuration.default_type,
                        self.path_argument_is_mandatory,
                        ['arg1', 'arg2']),
            Expectation(relativity=self.configuration.default_type,
                        remaining_arguments=['arg2'],
                        path_argument='arg1',
                        rel_option_type=self.configuration.rel_option_type),
        )
