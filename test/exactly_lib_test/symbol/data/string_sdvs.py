import unittest

from exactly_lib.symbol.data.impl import string_sdv_impls as impl
from exactly_lib_test.symbol.data.test_resources.concrete_value_assertions import equals_string_fragment_sdv


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestTransformedStringFragmentResolver),

    ])


class TestTransformedStringFragmentResolver(unittest.TestCase):
    def test(self):
        untransformed = impl.ConstantStringFragmentSdv('constant')
        expected = impl.ConstantStringFragmentSdv('CONSTANT')
        actual = impl.TransformedStringFragmentSdv(untransformed,
                                                   str.upper)

        equals_string_fragment_sdv(expected).apply_without_message(self, actual)
