import unittest

from exactly_lib_test.help.entities.concepts import concept_structure, configuration_parameters, render
from exactly_lib_test.help.entities.concepts import plain_concept


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        concept_structure.suite(),
        plain_concept.suite(),
        configuration_parameters.suite(),
        render.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
