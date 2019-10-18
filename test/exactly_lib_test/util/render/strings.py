import unittest

from exactly_lib.util.render import strings as sut
from exactly_lib.util.render.combinators import ConstantR, ConstantSequenceR
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestAsToString),
        unittest.makeSuite(TestJoiningOfElementRenderers),
        unittest.makeSuite(TestJoiningOfElementsRenderer),
    ])


class TestAsToString(unittest.TestCase):
    def test(self):
        # ARRANGE #

        renderer = ConstantR('the rendered string')
        to_string_object = sut.AsToStringObject(renderer)

        # ACT #

        actual = str(to_string_object)

        # ASSERT #

        expected = renderer.render()
        self.assertEqual(expected,
                         actual)


class TestJoiningOfElementRenderers(unittest.TestCase):

    def test_without_separator(self):
        # ARRANGE #
        for case in _CASES:
            with self.subTest(case.name):
                expected = ''.join(case.value)
                renderer = sut.JoiningOfElementRenderers([ConstantR(s) for s in case.value])

                # ACT #

                actual = renderer.render()

                # ASSERT #

                self.assertEqual(expected, actual)

    def test_with_separator(self):
        # ARRANGE #

        separator_string = 'separator'
        separator = ConstantR(separator_string)
        for case in _CASES:
            with self.subTest(case.name):
                expected = separator_string.join(case.value)
                renderer = sut.JoiningOfElementRenderers([ConstantR(s) for s in case.value],
                                                         separator)

                # ACT #

                actual = renderer.render()

                # ASSERT #

                self.assertEqual(expected, actual)


class TestJoiningOfElementsRenderer(unittest.TestCase):
    def test_without_separator(self):
        # ARRANGE #
        for case in _CASES:
            with self.subTest(case.name):
                expected = ''.join(case.value)
                renderer = sut.JoiningOfElementsRenderer(ConstantSequenceR(case.value))

                # ACT #

                actual = renderer.render()

                # ASSERT #

                self.assertEqual(expected, actual)

    def test_with_separator(self):
        # ARRANGE #

        separator_string = 'separator'
        separator = ConstantR(separator_string)
        for case in _CASES:
            with self.subTest(case.name):
                expected = separator_string.join(case.value)
                renderer = sut.JoiningOfElementsRenderer(ConstantSequenceR(case.value),
                                                         separator)

                # ACT #

                actual = renderer.render()

                # ASSERT #

                self.assertEqual(expected, actual)


_CASES = [
    NameAndValue('empty',
                 [],
                 ),
    NameAndValue('singleton',
                 ['string 1'],
                 ),
    NameAndValue('multiple',
                 ['string 1', 'string 2'],
                 ),
]
