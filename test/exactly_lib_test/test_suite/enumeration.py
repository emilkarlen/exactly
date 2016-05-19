import pathlib
import unittest

from exactly_lib.act_phase_setups import single_command_setup
from exactly_lib.cli.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.processing.preprocessor import IDENTITY_PREPROCESSOR
from exactly_lib.processing.test_case_processing import TestCaseSetup
from exactly_lib.test_suite.enumeration import DepthFirstEnumerator
from exactly_lib.test_suite.structure import TestSuite


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestDepthFirstEnumerator)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())

T_C_H_S = TestCaseHandlingSetup(single_command_setup.act_phase_setup(),
                                IDENTITY_PREPROCESSOR)


class TestDepthFirstEnumerator(unittest.TestCase):
    def test_single_suite(self):
        root_suite = TestSuite(
            pathlib.Path('root-file'),
            [],
            T_C_H_S,
            [],
            [TestCaseSetup(pathlib.Path('case-file'))])
        suite_list = DepthFirstEnumerator().apply(root_suite)
        self.assertEqual(1,
                         len(suite_list),
                         'Number of enumerated suites')
        self.assertIs(root_suite,
                      suite_list[0],
                      'Suite object')

    def test_hierarchy(self):
        # ARRANGE #
        sub11 = TestSuite(pathlib.Path('11'), [], T_C_H_S, [], [])
        sub12 = TestSuite(pathlib.Path('12'), [], T_C_H_S, [], [])
        sub1 = TestSuite(pathlib.Path('1'), [], T_C_H_S, [sub11, sub12], [])
        sub21 = TestSuite(pathlib.Path('21'), [], T_C_H_S, [], [])
        sub2 = TestSuite(pathlib.Path('2'), [], T_C_H_S, [sub21], [])
        root = TestSuite(pathlib.Path('root'), [], T_C_H_S, [sub1, sub2], [])
        # ACT #
        actual = DepthFirstEnumerator().apply(root)
        # ASSERT #
        expected = [
            sub11,
            sub12,
            sub1,
            sub21,
            sub2,
            root,
        ]
        self.assertEqual(len(expected),
                         len(actual),
                         'Number of enumerated suites')
        for e, a in zip(expected, actual):
            self.assertIs(e,
                          a,
                          'Suite object')
