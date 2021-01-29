import unittest

from exactly_lib_test.impls.instructions.assert_.stdout_err.test_resources import program_output
from exactly_lib_test.impls.instructions.assert_.stdout_err.test_resources.configuration_for_contents_of_act_result import \
    TestConfigurationForStdFile
from exactly_lib_test.impls.instructions.assert_.stdout_err.test_resources.program_output.configuration import \
    ProgramOutputInstructionConfiguration
from exactly_lib_test.impls.instructions.assert_.test_resources.file_contents import common_tests


def suite_for(configuration: TestConfigurationForStdFile,
              channel_configuration: ProgramOutputInstructionConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        common_tests.suite_for(configuration),
        program_output.suite_for(channel_configuration),
    ])
