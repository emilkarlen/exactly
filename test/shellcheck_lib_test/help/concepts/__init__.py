import unittest

from shellcheck_lib_test.help.concepts import concept_structure, concept, configuration_parameters


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        concept_structure.suite(),
        concept.suite(),
        configuration_parameters.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
