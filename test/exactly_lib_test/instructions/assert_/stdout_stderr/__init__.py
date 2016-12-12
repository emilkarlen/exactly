import unittest

from exactly_lib.instructions.assert_ import stdout_stderr as sut
from exactly_lib_test.instructions.assert_.stdout_stderr import contains, empty, equals
from exactly_lib_test.instructions.assert_.stdout_stderr.test_resources import TestWithParserBase
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([

        empty.suite(),
        equals.suite(),
        contains.suite(),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name', 'file')),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
