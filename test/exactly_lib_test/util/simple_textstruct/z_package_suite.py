import unittest

from exactly_lib_test.util.simple_textstruct.test_resources_test import structure_assertions


def suite() -> unittest.TestSuite:
    return structure_assertions.suite()
