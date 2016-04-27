import unittest

from exactly_lib.help.concepts import concept as sut
from exactly_lib_test.help.concepts.test_resources import suite_for_plain_concept_documentation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_plain_concept_documentation(sut.SANDBOX_CONCEPT),
        suite_for_plain_concept_documentation(sut.CONFIGURATION_PARAMETER_CONCEPT),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
