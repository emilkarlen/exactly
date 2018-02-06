import unittest

from exactly_lib_test.instructions.assert_ import \
    change_dir, \
    contents_of_file, \
    contents_of_dir, \
    run, \
    exitcode, \
    new_file, \
    new_dir, \
    shell, \
    existence_of_file, \
    env, \
    utils
from exactly_lib_test.instructions.assert_ import stdout, stderr
from exactly_lib_test.instructions.assert_ import test_resources


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources.suite(),
        utils.suite(),
        exitcode.suite(),
        contents_of_file.suite(),
        contents_of_dir.suite(),
        stdout.suite(),
        stderr.suite(),
        existence_of_file.suite(),
        new_file.suite(),
        new_dir.suite(),
        change_dir.suite(),
        run.suite(),
        shell.suite(),
        env.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
