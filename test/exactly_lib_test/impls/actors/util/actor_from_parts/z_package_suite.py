import unittest

from exactly_lib_test.impls.actors.util.actor_from_parts import main


def suite() -> unittest.TestSuite:
    return main.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
