import unittest

from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.program_output import empty
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.program_output.configuration import \
    ChannelConfiguration


def suite_for(conf: ChannelConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        empty.suite_for(conf),
    ])
