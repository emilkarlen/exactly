import unittest

from exactly_lib.help.actors.actor.all_actors import ALL_ACTORS
from exactly_lib_test.help.actors.test_resources.test_case_impls import suite_for_actor_documentation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
                                  suite_for_actor_documentation(actor_doc)
                                  for actor_doc in ALL_ACTORS
                                  ])


def run_suite():
    unittest.TextTestRunner().run(suite())


if __name__ == '__main__':
    run_suite()
