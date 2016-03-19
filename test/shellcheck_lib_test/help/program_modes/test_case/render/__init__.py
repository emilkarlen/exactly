import unittest

from shellcheck_lib_test.help.program_modes.test_case.render import render_instruction


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(render_instruction.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
