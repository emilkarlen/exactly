import unittest

from exactly_lib_test.util.simple_textstruct.test_resources_test import structure_assertions, renderer_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        structure_assertions.suite(),
        renderer_assertions.suite(),
    ])
