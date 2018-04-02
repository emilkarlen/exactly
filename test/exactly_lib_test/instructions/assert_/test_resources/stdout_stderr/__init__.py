import unittest

from exactly_lib_test.instructions.assert_.test_resources.file_contents import common_tests
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr import program_output
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.configuration_for_contents_of_act_result import \
    TestConfigurationForStdFile
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.program_output.configuration import \
    ProgramOutputInstructionConfiguration


def suite_for(configuration: TestConfigurationForStdFile,
              channel_configuration: ProgramOutputInstructionConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        common_tests.suite_for(configuration),
        program_output.suite_for(channel_configuration),
    ])
