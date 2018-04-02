import unittest

from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.program_output import common, empty
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.program_output.configuration import \
    ProgramOutputInstructionConfiguration


def suite_for(conf: ProgramOutputInstructionConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        common.suite_for(conf),
        empty.suite_for(conf),
    ])
