import unittest

from exactly_lib_test.test_resources_test.value_assertions import value_assertion, xml_etree


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        value_assertion.suite(),
        xml_etree.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
