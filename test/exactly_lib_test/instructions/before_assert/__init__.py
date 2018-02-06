import unittest

from exactly_lib_test.instructions.before_assert import test_resources, utils, \
    change_dir, env, run, shell, new_file, new_dir


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources.suite(),
        utils.suite(),
        change_dir.suite(),
        new_file.suite(),
        new_dir.suite(),
        shell.suite(),
        run.suite(),
        env.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
