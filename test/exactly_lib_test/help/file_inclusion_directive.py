import unittest

from exactly_lib.help import file_inclusion_directive as sut
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation


def suite() -> unittest.TestSuite:
    return suite_for_instruction_documentation(sut.FileInclusionDirectiveDocumentation())
