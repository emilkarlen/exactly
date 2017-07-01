import unittest

from exactly_lib.execution.symbols_handling import restriction_failure_renderer as sut
from exactly_lib.symbol.concrete_restrictions import FailureOfDirectReference, FailureOfIndirectReference


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestRenderFailureOfDirectReference),
        unittest.makeSuite(TestRenderFailureOfIndirectReference),
    ])


class TestRenderFailureOfDirectReference(unittest.TestCase):
    def test(self):
        # ARRANGE #
        failure = FailureOfDirectReference('error message')
        # ACT #
        actual = sut.error_message(failure)
        # ASSERT #
        self.assertIsInstance(actual, str)


class TestRenderFailureOfIndirectReference(unittest.TestCase):
    def test(self):
        # ARRANGE #
        failure = FailureOfIndirectReference('error message')
        # ACT #
        actual = sut.error_message(failure)
        # ASSERT #
        self.assertIsInstance(actual, str)
