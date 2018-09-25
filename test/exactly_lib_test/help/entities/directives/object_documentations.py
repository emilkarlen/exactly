import unittest

from exactly_lib.help.entities.directives import all_directives
from exactly_lib_test.help.entities.directives.test_resources.test_case_impls import suite_for_directive_documentation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_directive_documentation(actor_doc)
        for actor_doc in all_directives.all_directives()
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
