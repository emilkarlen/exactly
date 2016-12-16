import unittest

from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfiguration
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    RelativityOptionConfiguration
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    RelativityOptionConfigurationForRelCwd, RelativityOptionConfigurationForRelAct, \
    RelativityOptionConfigurationForRelTmp

RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE = [
    RelativityOptionConfigurationForRelCwd(),
    RelativityOptionConfigurationForRelAct(),
    RelativityOptionConfigurationForRelTmp(),
    # Test of default relativity is done by "generic" tests of equals -
    # i.e. code in the test resources that are used for all content-checking instructions.
]


def suite_for_all_relativity_options(instruction_configuration: InstructionTestConfiguration,
                                     test_cases: list) -> unittest.TestSuite:
    def suite_for_option(option_configuration: RelativityOptionConfiguration) -> unittest.TestSuite:
        return unittest.TestSuite([tc(instruction_configuration, option_configuration)
                                   for tc in test_cases])

    return unittest.TestSuite([suite_for_option(relativity_option_configuration)
                               for relativity_option_configuration in RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE])
