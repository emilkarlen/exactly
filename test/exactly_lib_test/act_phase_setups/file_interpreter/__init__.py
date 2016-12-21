import unittest

from exactly_lib_test.act_phase_setups.file_interpreter import act_phase_contents


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(act_phase_contents.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
