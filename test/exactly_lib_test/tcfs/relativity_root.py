import unittest

from exactly_lib.tcfs import relativity_root as sut
from exactly_lib_test.tcfs.test_resources import relativity_test_utils as utils
from exactly_lib_test.tcfs.test_resources.relativity_test_utils import sds_2_act_dir, \
    sds_2_result_dir, sds_2_tmp_user_dir, tcds_2_hds_case_dir, tcds_2_cwd_dir, hds_2_hds_case_dir


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestHdsRelativityResolver),
        unittest.makeSuite(TestSdsRelativityResolver),
        unittest.makeSuite(TestNonHdsRelativityResolver),
        unittest.makeSuite(TestAnyRelativityResolver),
    ])


class TestHdsRelativityResolver(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName)
        self.helper = utils.HdsRelativityResolverHelper(self)

    def test(self):
        cases = [
            (sut.RelHdsOptionType.REL_HDS_CASE, sut.resolver_for_hds_case, hds_2_hds_case_dir),
        ]
        for rel_option_type, resolver, expected_root_path_resolver in cases:
            with self.subTest(rel_option_type=str(rel_option_type)):
                self.helper.check(resolver,
                                  rel_option_type,
                                  expected_root_path_resolver)


class TestSdsRelativityResolver(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName)
        self.helper = utils.SdsRelativityResolverHelper(self)

    def test(self):
        cases = [
            (sut.RelSdsOptionType.REL_RESULT, sut.resolver_for_result, sds_2_result_dir),
            (sut.RelSdsOptionType.REL_ACT, sut.resolver_for_act, sds_2_act_dir),
            (sut.RelSdsOptionType.REL_TMP, sut.resolver_for_tmp_user, sds_2_tmp_user_dir),
        ]
        for rel_option_type, resolver, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                self.helper.check(resolver,
                                  rel_option_type,
                                  expected_root_path_resolver)


class TestNonHdsRelativityResolver(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName)
        self.helper = utils.NonHdsRelativityResolverHelper(self)

    def test_under_sds(self):
        cases = [
            (sut.RelNonHdsOptionType.REL_RESULT, sut.resolver_for_result, sds_2_result_dir),
            (sut.RelNonHdsOptionType.REL_ACT, sut.resolver_for_act, sds_2_act_dir),
            (sut.RelNonHdsOptionType.REL_TMP, sut.resolver_for_tmp_user, sds_2_tmp_user_dir),
        ]
        for rel_option_type, resolver, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                self.helper.check_under_sds(resolver,
                                            rel_option_type,
                                            expected_root_path_resolver)

    def test_cwd(self):
        cases = [
            (sut.RelNonHdsOptionType.REL_CWD, sut.resolver_for_cwd, tcds_2_cwd_dir),
        ]
        for rel_option_type, resolver, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                self.helper.check_cwd(resolver,
                                      rel_option_type,
                                      expected_root_path_resolver)


class TestAnyRelativityResolver(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName)
        self.helper = utils.AnyRelativityResolverHelper(self)

    def test_under_sds(self):
        cases = [
            (sut.RelOptionType.REL_RESULT, sut.resolver_for_result, sds_2_result_dir),
            (sut.RelOptionType.REL_ACT, sut.resolver_for_act, sds_2_act_dir),
            (sut.RelOptionType.REL_TMP, sut.resolver_for_tmp_user, sds_2_tmp_user_dir),
        ]
        for rel_option_type, resolver, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                self.helper.check_under_sds(resolver,
                                            rel_option_type,
                                            expected_root_path_resolver)

    def test_under_hds(self):
        cases = [
            (sut.RelOptionType.REL_HDS_CASE, sut.resolver_for_hds_case, tcds_2_hds_case_dir),
        ]
        for rel_option_type, resolver, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                self.helper.check_under_hds(resolver,
                                            rel_option_type,
                                            expected_root_path_resolver)

    def test_cwd(self):
        cases = [
            (sut.RelOptionType.REL_CWD, sut.resolver_for_cwd, tcds_2_cwd_dir),
        ]
        for rel_option_type, resolver, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                self.helper.check_cwd(resolver,
                                      rel_option_type,
                                      expected_root_path_resolver)
