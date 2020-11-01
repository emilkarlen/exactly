import unittest

from exactly_lib.tcfs import tcds as sut
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_sds, fake_hds


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_construct_and_get_hds(self):
        # ARRANGE #
        expected_hds = fake_hds()
        sds = fake_sds()
        # ACT #
        tcds = sut.TestCaseDs(expected_hds, sds)
        actual = tcds.hds
        # ASSERT #
        self.assertIs(actual, expected_hds)

    def test_construct_and_get_sds(self):
        # ARRANGE #
        expected_hds = fake_hds()
        sds = fake_sds()
        # ACT #
        tcds = sut.TestCaseDs(expected_hds, sds)
        actual = tcds.sds
        # ASSERT #
        self.assertIs(actual, sds)
