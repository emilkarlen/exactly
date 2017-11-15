import unittest

from exactly_lib.help.entities.concepts.all_concepts import all_concepts
from exactly_lib_test.help.entities.concepts.test_resources import suite_for_concept_documentation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([suite_for_concept_documentation(doc)
                               for doc in all_concepts()])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
