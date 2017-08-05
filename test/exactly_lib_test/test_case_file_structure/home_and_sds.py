import unittest

from exactly_lib.test_case_file_structure import home_and_sds as sut
from exactly_lib_test.test_case_file_structure.test_resources.paths import dummy_sds, dummy_hds


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_construct_and_get_hds(self):
        # ARRANGE #
        expected_hds = dummy_hds()
        sds = dummy_sds()
        # ACT #
        home_and_sds = sut.HomeAndSds(expected_hds, sds)
        actual = home_and_sds.hds
        # ASSERT #
        self.assertIs(actual, expected_hds)

    def test_construct_and_get_sds(self):
        # ARRANGE #
        expected_hds = dummy_hds()
        sds = dummy_sds()
        # ACT #
        home_and_sds = sut.HomeAndSds(expected_hds, sds)
        actual = home_and_sds.sds
        # ASSERT #
        self.assertIs(actual, sds)
