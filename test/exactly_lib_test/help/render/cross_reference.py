import unittest

from exactly_lib.help.render import cross_reference as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_predefined_contents_part(self):
        # ARRANGE #
        constructor = sut.CrossReferenceTextConstructor()

        for part in sut.HelpPredefinedContentsPart:
            with self.subTest(part):
                target = sut.PredefinedHelpContentsPartReference(part)
                # ACT #
                actual = constructor.apply(target)
                # ASSERT #
                self.assertIsInstance(actual, sut.CrossReferenceText)
                self.assertEqual(-1,
                                 actual.title_text.value.find('exactly_lib'),
                                 'Rendered text should not contain auto gen string rep of source code')
