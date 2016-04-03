import unittest

from shellcheck_lib.help.concepts import render as sut
from shellcheck_lib.help.concepts.all_concepts import all_concepts
from shellcheck_lib.help.program_modes.test_case.contents_structure import ConceptsHelp
from shellcheck_lib_test.util.textformat.test_resources import structure as struct_check


class TestAllConceptsList(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        renderer = sut.AllConceptsListRenderer(ConceptsHelp(all_concepts()))
        # ACT #
        actual = renderer.apply()
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestAllConceptsList),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
