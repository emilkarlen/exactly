import unittest

from exactly_lib.util.textformat.constructor import paragraphs as sut
from exactly_lib.util.textformat.structure.core import StringText
from exactly_lib.util.textformat.structure.paragraph import Paragraph
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.textformat.constructor.test_resources import CONSTRUCTION_ENVIRONMENT


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestConstant),
        unittest.makeSuite(TestSequence),
    ])


class TestConstant(unittest.TestCase):
    def test(self):
        # ARRANGE #
        const_pi = Paragraph([])
        cases = [
            NEA('empty sequence of paragraphs',
                expected=asrt.matches_sequence([]),
                actual=[]
                ),
            NEA('single paragraph',
                expected=asrt.matches_sequence([
                    asrt.is__any(const_pi)
                ]),
                actual=[const_pi]
                ),
        ]

        for case in cases:
            with self.subTest(case.name):
                # ACT #

                actual = sut.constant(case.actual).apply(CONSTRUCTION_ENVIRONMENT)

                # ASSERT #

                case.expected.apply_without_message(self, actual)


class TestSequence(unittest.TestCase):
    def test(self):
        # ARRANGE #
        const_pi_1 = Paragraph([])
        const_pi_2 = Paragraph([StringText('const pi 2')])
        const_pi_3 = Paragraph([StringText('const pi 3')])
        cases = [
            NEA('empty sequence of paragraphs',
                expected=asrt.matches_sequence([]),
                actual=[]
                ),
            NEA('single constructor',
                expected=asrt.matches_sequence([
                    asrt.is__any(const_pi_1)
                ]),
                actual=[sut.constant([const_pi_1])]
                ),
            NEA('multiple constructors',
                expected=asrt.matches_sequence([
                    asrt.is__any(const_pi_1),
                    asrt.is__any(const_pi_2),
                    asrt.is__any(const_pi_3),
                ]),
                actual=[sut.constant([const_pi_1,
                                      const_pi_2]),
                        sut.constant([const_pi_3])]
                ),
        ]

        for case in cases:
            with self.subTest(case.name):
                # ACT #

                actual = sut.sequence(case.actual).apply(CONSTRUCTION_ENVIRONMENT)

                # ASSERT #

                case.expected.apply_without_message(self, actual)
