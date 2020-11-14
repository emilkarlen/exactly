import unittest

from exactly_lib_test.test_resources_test.source import layout, token_sequence


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        layout.suite(),
        token_sequence.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
