import unittest

from exactly_lib_test.impls.actors.source_interpreter import interpreter_behaviour
from exactly_lib_test.impls.actors.source_interpreter import symbols_and_validation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        symbols_and_validation.suite(),
        interpreter_behaviour.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
