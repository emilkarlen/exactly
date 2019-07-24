import unittest

from exactly_lib_test.util.simple_textstruct import structure
from exactly_lib_test.util.simple_textstruct.test_resources_test import structure_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        structure.suite(),
        structure_assertions.suite(),
    ])
