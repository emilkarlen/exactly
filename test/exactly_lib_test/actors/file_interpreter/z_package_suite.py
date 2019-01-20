import unittest

from exactly_lib_test.actors.file_interpreter import executable_file, shell_command


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        executable_file.suite(),
        shell_command.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
