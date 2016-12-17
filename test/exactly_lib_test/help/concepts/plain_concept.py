import unittest

from exactly_lib.help.concepts.plain_concepts.all_plain_concepts import all_plain_concepts
from exactly_lib_test.help.concepts.test_resources.test_case_impls import suite_for_plain_concept_documentation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([suite_for_plain_concept_documentation(plain_concept)
                               for plain_concept in all_plain_concepts()])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
