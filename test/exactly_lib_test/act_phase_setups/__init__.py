import unittest

from exactly_lib_test.act_phase_setups import script_language_setup, single_command_setup


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(script_language_setup.suite())
    ret_val.addTest(single_command_setup.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
