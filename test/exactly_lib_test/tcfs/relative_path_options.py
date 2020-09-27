import unittest

from exactly_lib.tcfs import relative_path_options as sut
from exactly_lib_test.tcfs.test_resources import relativity_test_utils as dir_fun
from exactly_lib_test.tcfs.test_resources import relativity_test_utils as utils


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

    def test_resolvers(self):
        cases = [
            (sut.RelHdsOptionType.REL_HDS_CASE, dir_fun.hds_2_hds_case_dir),
            (sut.RelHdsOptionType.REL_HDS_ACT, dir_fun.hds_2_hds_act_dir),
        ]
        for rel_option_type, expected_root_path_resolver in cases:
            resolver = sut.REL_HDS_OPTIONS_MAP[rel_option_type].root_resolver
            with self.subTest(msg=str(rel_option_type)):
                self.helper.check(resolver,
                                  rel_option_type,
                                  expected_root_path_resolver)

    def test_dict_keys(self):
        expected = {
            sut.RelHdsOptionType.REL_HDS_CASE,
            sut.RelHdsOptionType.REL_HDS_ACT,
        }
        self.assertEqual(expected,
                         sut.REL_HDS_OPTIONS_MAP.keys())


class TestSdsRelativityResolver(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName)
        self.helper = utils.SdsRelativityResolverHelper(self)

    def test(self):
        cases = [
            (sut.RelSdsOptionType.REL_RESULT, dir_fun.sds_2_result_dir),
            (sut.RelSdsOptionType.REL_ACT, dir_fun.sds_2_act_dir),
            (sut.RelSdsOptionType.REL_TMP, dir_fun.sds_2_tmp_user_dir),
        ]
        for rel_option_type, expected_root_path_resolver in cases:
            resolver = sut.REL_SDS_OPTIONS_MAP[rel_option_type].root_resolver
            with self.subTest(msg=str(rel_option_type)):
                self.helper.check(resolver,
                                  rel_option_type,
                                  expected_root_path_resolver)

    def test_dict_keys(self):
        expected = {
            sut.RelSdsOptionType.REL_ACT,
            sut.RelSdsOptionType.REL_RESULT,
            sut.RelSdsOptionType.REL_TMP,
        }
        self.assertEqual(expected,
                         sut.REL_SDS_OPTIONS_MAP.keys())


class TestNonHdsRelativityResolver(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName)
        self.helper = utils.NonHdsRelativityResolverHelper(self)

    def test_under_sds(self):
        cases = [
            (sut.RelNonHdsOptionType.REL_RESULT, dir_fun.sds_2_result_dir),
            (sut.RelNonHdsOptionType.REL_ACT, dir_fun.sds_2_act_dir),
            (sut.RelNonHdsOptionType.REL_TMP, dir_fun.sds_2_tmp_user_dir),
        ]
        for rel_option_type, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                resolver = sut.REL_NON_HDS_OPTIONS_MAP[rel_option_type].root_resolver
                self.helper.check_under_sds(resolver,
                                            rel_option_type,
                                            expected_root_path_resolver)

    def test_cwd(self):
        cases = [
            (sut.RelNonHdsOptionType.REL_CWD, dir_fun.tcds_2_cwd_dir),
        ]
        for rel_option_type, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                resolver = sut.REL_NON_HDS_OPTIONS_MAP[rel_option_type].root_resolver
                self.helper.check_cwd(resolver,
                                      rel_option_type,
                                      expected_root_path_resolver)

    def test_dict_keys(self):
        expected = {
            sut.RelNonHdsOptionType.REL_ACT,
            sut.RelNonHdsOptionType.REL_RESULT,
            sut.RelNonHdsOptionType.REL_TMP,
            sut.RelNonHdsOptionType.REL_CWD,
        }
        self.assertEqual(expected,
                         sut.REL_NON_HDS_OPTIONS_MAP.keys())


class TestAnyRelativityResolver(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName)
        self.helper = utils.AnyRelativityResolverHelper(self)

    def test_under_sds(self):
        cases = [
            (sut.RelOptionType.REL_RESULT, dir_fun.sds_2_result_dir),
            (sut.RelOptionType.REL_ACT, dir_fun.sds_2_act_dir),
            (sut.RelOptionType.REL_TMP, dir_fun.sds_2_tmp_user_dir),
        ]
        for rel_option_type, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                resolver = sut.REL_OPTIONS_MAP[rel_option_type].root_resolver
                self.helper.check_under_sds(resolver,
                                            rel_option_type,
                                            expected_root_path_resolver)

    def test_under_hds(self):
        cases = [
            (sut.RelOptionType.REL_HDS_CASE, dir_fun.tcds_2_hds_case_dir),
            (sut.RelOptionType.REL_HDS_ACT, dir_fun.tcds_2_hds_act_dir),
        ]
        for rel_option_type, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                resolver = sut.REL_OPTIONS_MAP[rel_option_type].root_resolver
                self.helper.check_under_hds(resolver,
                                            rel_option_type,
                                            expected_root_path_resolver)

    def test_cwd(self):
        cases = [
            (sut.RelOptionType.REL_CWD, dir_fun.tcds_2_cwd_dir),
        ]
        for rel_option_type, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                resolver = sut.REL_OPTIONS_MAP[rel_option_type].root_resolver
                self.helper.check_cwd(resolver,
                                      rel_option_type,
                                      expected_root_path_resolver)

    def test_dict_keys(self):
        expected = {
            sut.RelOptionType.REL_HDS_CASE,
            sut.RelOptionType.REL_HDS_ACT,
            sut.RelOptionType.REL_ACT,
            sut.RelOptionType.REL_RESULT,
            sut.RelOptionType.REL_TMP,
            sut.RelOptionType.REL_CWD,
        }
        self.assertEqual(expected,
                         sut.REL_OPTIONS_MAP.keys())
