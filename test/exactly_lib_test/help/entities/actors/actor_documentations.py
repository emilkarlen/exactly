import unittest

from exactly_lib.help.entities.actors import all_actor_docs
from exactly_lib_test.help.entities.actors.test_resources.test_case_impls import suite_for_actor_documentation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_actor_documentation(actor_doc)
        for actor_doc in all_actor_docs.ALL_ACTOR_DOCS
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
