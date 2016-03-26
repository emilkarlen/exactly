import unittest

from shellcheck_lib_test.help.program_modes.test_case.render import render_instruction, main_documentation


def suite():
    return unittest.TestSuite([
        render_instruction.suite(),
        main_documentation.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
