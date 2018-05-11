import unittest

from exactly_lib_test.type_system.logic.string_transformer import identity, sequence


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        identity.suite(),
        sequence.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
