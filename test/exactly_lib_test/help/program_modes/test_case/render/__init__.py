import unittest

from exactly_lib_test.help.program_modes.test_case.render import main_documentation


def suite():
    return unittest.TestSuite([
        main_documentation.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
