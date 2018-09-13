import unittest

from exactly_lib_test.util.textformat import parse, utils
from exactly_lib_test.util.textformat.construction import z_package_suite as construction
from exactly_lib_test.util.textformat.rendering import z_package_suite as rendering
from exactly_lib_test.util.textformat.structure import z_package_suite as structure


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        rendering.suite(),
        structure.suite(),
        parse.suite(),
        utils.suite(),
        construction.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
