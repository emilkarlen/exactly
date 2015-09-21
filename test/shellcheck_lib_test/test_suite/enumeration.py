import pathlib
import unittest

from shellcheck_lib.test_case.preprocessor import IDENTITY_PREPROCESSOR
from shellcheck_lib.test_suite.enumeration import DepthFirstEnumerator
from shellcheck_lib.test_suite.structure import TestSuite
from shellcheck_lib.test_case.test_case_processing import TestCaseSetup

IP = IDENTITY_PREPROCESSOR


class TestDepthFirstEnumerator(unittest.TestCase):
    def test_single_suite(self):
        root_suite = TestSuite(
            pathlib.Path('root-file'),
            [],
            IP,
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
        sub11 = TestSuite(pathlib.Path('11'), [], IP, [], [])
        sub12 = TestSuite(pathlib.Path('12'), [], IP, [], [])
        sub1 = TestSuite(pathlib.Path('1'), [], IP, [sub11, sub12], [])
        sub21 = TestSuite(pathlib.Path('21'), [], IP, [], [])
        sub2 = TestSuite(pathlib.Path('2'), [], IP, [sub21], [])
        root = TestSuite(pathlib.Path('root'), [], IP, [sub1, sub2], [])
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


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestDepthFirstEnumerator))
    return ret_val


if __name__ == '__main__':
    unittest.main()
