import unittest

from exactly_lib_test.instructions.assert_.test_resources.file_contents import contains
from exactly_lib_test.instructions.assert_.test_resources.file_contents import empty
from exactly_lib_test.instructions.assert_.test_resources.file_contents import equals
from exactly_lib_test.instructions.assert_.test_resources.file_contents.equals import \
    InstructionTestConfigurationForEquals


def suite_for(configuration: InstructionTestConfigurationForEquals) -> unittest.TestSuite:
    return unittest.TestSuite([
        empty.suite_for(configuration),
        equals.suite_for(configuration),
        contains.suite_for(configuration),

    ])
