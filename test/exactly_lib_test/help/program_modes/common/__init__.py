import unittest

from exactly_lib_test.help.program_modes.common import render_instruction


def suite():
    return unittest.TestSuite([
        render_instruction.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
