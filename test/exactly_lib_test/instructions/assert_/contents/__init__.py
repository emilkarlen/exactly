import unittest

from exactly_lib.instructions.assert_ import contents as sut
from exactly_lib_test.instructions.assert_.contents import empty, equals, parse
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        parse.suite(),
        empty.suite(),
        equals.suite(),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
