import unittest

from exactly_lib_test.instructions.multi_phase.run_program import run, instruction_embryo


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        run.suite(),
        instruction_embryo.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
