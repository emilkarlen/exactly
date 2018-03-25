import unittest

from exactly_lib.symbol.data.impl import string_resolver_impls as impl
from exactly_lib_test.symbol.data.test_resources.concrete_value_assertions import equals_string_fragment_resolver


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestTransformedStringFragmentResolver),

    ])


class TestTransformedStringFragmentResolver(unittest.TestCase):
    def test(self):
        untransformed = impl.ConstantStringFragmentResolver('constant')
        expected = impl.ConstantStringFragmentResolver('CONSTANT')
        actual = impl.TransformedStringFragmentResolver(untransformed,
                                                        str.upper)

        equals_string_fragment_resolver(expected).apply_without_message(self, actual)
