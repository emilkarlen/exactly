import unittest

from exactly_lib_test.act_phase_setups.util.executor_made_of_parts import main


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(main.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
