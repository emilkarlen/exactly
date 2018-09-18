import unittest

from exactly_lib.cli.program_modes.help.request_handling import console_help as sut
from exactly_lib.definitions.cross_ref.concrete_cross_refs import HelpPredefinedContentsPart
from exactly_lib.util.textformat.structure.core import CrossReferenceText, StringText


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(HelpCrossReferenceFormatterTest)


class HelpCrossReferenceFormatterTest(unittest.TestCase):
    def test_predefined_contents_part(self):
        # ARRANGE #
        constructor = sut.HelpCrossReferenceFormatter()

        for part in HelpPredefinedContentsPart:
            with self.subTest(part):
                target = sut.PredefinedHelpContentsPartReference(part)
                cross_ref_text = CrossReferenceText(StringText('The title'),
                                                    target)
                # ACT #
                actual = constructor.apply(cross_ref_text)
                # ASSERT #
                self.assertIsInstance(actual, str)
                self.assertEqual(-1,
                                 actual.find('exactly_lib'),
                                 'Rendered text should not contain auto gen string rep of source code')
