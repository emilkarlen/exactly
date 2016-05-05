import unittest

from exactly_lib_test.help.concepts import concept_structure, plain_concept, configuration_parameters, render


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        concept_structure.suite(),
        plain_concept.suite(),
        configuration_parameters.suite(),
        render.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
