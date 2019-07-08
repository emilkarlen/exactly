import unittest

from exactly_lib_test.type_system.trace.test_resources_test import trace_assertions, trace_rendering_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        trace_assertions.suite(),
        trace_rendering_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
