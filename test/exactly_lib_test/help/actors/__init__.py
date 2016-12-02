import unittest

from exactly_lib_test.help.actors import actor_documentations


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        actor_documentations.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
