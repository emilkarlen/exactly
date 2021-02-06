import unittest

from exactly_lib.impls.instructions.assert_ import contents_of_file as sut
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.impls.instructions.assert_.contents_of_file import parse
from exactly_lib_test.impls.instructions.assert_.contents_of_file import specific
from exactly_lib_test.impls.instructions.assert_.contents_of_file.test_resources.instruction_configuration import \
    TestConfigurationForFile
from exactly_lib_test.impls.instructions.assert_.test_resources.file_contents import common_tests


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        common_tests.suite_for(TestConfigurationForFile()),

        parse.suite(),
        specific.suite(),

        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
