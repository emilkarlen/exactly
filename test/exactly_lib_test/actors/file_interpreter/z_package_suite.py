import unittest

from exactly_lib_test.actors.file_interpreter import configuration
from exactly_lib_test.actors.file_interpreter import interpreter_behaviour
from exactly_lib_test.actors.file_interpreter import symbols_and_validation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        interpreter_behaviour.suite(),
        symbols_and_validation.suite_for(configuration.COMMAND_THAT_RUNS_PYTHON_PROGRAM_FILE)
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
