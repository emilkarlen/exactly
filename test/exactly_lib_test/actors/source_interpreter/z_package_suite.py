import unittest

from exactly_lib.actors.source_interpreter import actor as sut
from exactly_lib_test.actors.source_interpreter import interpreter_behaviour
from exactly_lib_test.actors.source_interpreter import symbols_and_validation
from exactly_lib_test.actors.test_resources import python3


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        symbols_and_validation.suite_for(sut.actor(python3.python_command())),
        interpreter_behaviour.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
