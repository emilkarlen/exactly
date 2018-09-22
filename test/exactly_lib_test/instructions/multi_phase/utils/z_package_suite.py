import unittest

from exactly_lib_test.instructions.multi_phase.utils import instruction_embryo


def suite() -> unittest.TestSuite:
    return instruction_embryo.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
