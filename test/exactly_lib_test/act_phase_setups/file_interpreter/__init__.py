import unittest

from exactly_lib_test.act_phase_setups.file_interpreter import executable_file


def suite() -> unittest.TestSuite:
    tests = []
    tests.append(executable_file.suite())
    return unittest.TestSuite(tests)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
