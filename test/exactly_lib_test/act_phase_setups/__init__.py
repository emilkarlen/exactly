import unittest

from exactly_lib_test.act_phase_setups import script_language_setup, single_command_setup


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(script_language_setup.suite())
    ret_val.addTest(single_command_setup.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
