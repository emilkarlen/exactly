import unittest

from exactly_lib.test_case_file_structure import relative_path_options as sut
from exactly_lib_test.test_case_file_structure.test_resources import relativity_test_utils as utils
from exactly_lib_test.test_case_file_structure.test_resources.relativity_test_utils import sds_2_act_dir, \
    sds_2_result_dir, sds_2_tmp_user_dir, home_and_sds_2_home_case_dir, home_and_sds_2_cwd_dir, hds_2_case_dir


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestHomeRelativityResolver),
        unittest.makeSuite(TestSdsRelativityResolver),
        unittest.makeSuite(TestNonHomeRelativityResolver),
        unittest.makeSuite(TestAnyRelativityResolver),
    ])


class TestHomeRelativityResolver(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName)
        self.helper = utils.HomeRelativityResolverHelper(self)

    def test_resolvers(self):
        cases = [
            (sut.RelHomeOptionType.REL_HOME_CASE, hds_2_case_dir),
        ]
        for rel_option_type, expected_root_path_resolver in cases:
            resolver = sut.REL_HOME_OPTIONS_MAP[rel_option_type].root_resolver
            with self.subTest(msg=str(rel_option_type)):
                self.helper.check(resolver,
                                  rel_option_type,
                                  expected_root_path_resolver)

    def test_dict_keys(self):
        expected = {
            sut.RelHomeOptionType.REL_HOME_CASE,
        }
        self.assertEqual(expected,
                         sut.REL_HOME_OPTIONS_MAP.keys())


class TestSdsRelativityResolver(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName)
        self.helper = utils.SdsRelativityResolverHelper(self)

    def test(self):
        cases = [
            (sut.RelSdsOptionType.REL_RESULT, sds_2_result_dir),
            (sut.RelSdsOptionType.REL_ACT, sds_2_act_dir),
            (sut.RelSdsOptionType.REL_TMP, sds_2_tmp_user_dir),
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


class TestNonHomeRelativityResolver(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName)
        self.helper = utils.NonHomeRelativityResolverHelper(self)

    def test_under_sds(self):
        cases = [
            (sut.RelNonHomeOptionType.REL_RESULT, sds_2_result_dir),
            (sut.RelNonHomeOptionType.REL_ACT, sds_2_act_dir),
            (sut.RelNonHomeOptionType.REL_TMP, sds_2_tmp_user_dir),
        ]
        for rel_option_type, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                resolver = sut.REL_NON_HOME_OPTIONS_MAP[rel_option_type].root_resolver
                self.helper.check_under_sds(resolver,
                                            rel_option_type,
                                            expected_root_path_resolver)

    def test_cwd(self):
        cases = [
            (sut.RelNonHomeOptionType.REL_CWD, home_and_sds_2_cwd_dir),
        ]
        for rel_option_type, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                resolver = sut.REL_NON_HOME_OPTIONS_MAP[rel_option_type].root_resolver
                self.helper.check_cwd(resolver,
                                      rel_option_type,
                                      expected_root_path_resolver)

    def test_dict_keys(self):
        expected = {
            sut.RelNonHomeOptionType.REL_ACT,
            sut.RelNonHomeOptionType.REL_RESULT,
            sut.RelNonHomeOptionType.REL_TMP,
            sut.RelNonHomeOptionType.REL_CWD,
        }
        self.assertEqual(expected,
                         sut.REL_NON_HOME_OPTIONS_MAP.keys())


class TestAnyRelativityResolver(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName)
        self.helper = utils.AnyRelativityResolverHelper(self)

    def test_under_sds(self):
        cases = [
            (sut.RelOptionType.REL_RESULT, sds_2_result_dir),
            (sut.RelOptionType.REL_ACT, sds_2_act_dir),
            (sut.RelOptionType.REL_TMP, sds_2_tmp_user_dir),
        ]
        for rel_option_type, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                resolver = sut.REL_OPTIONS_MAP[rel_option_type].root_resolver
                self.helper.check_under_sds(resolver,
                                            rel_option_type,
                                            expected_root_path_resolver)

    def test_under_home(self):
        cases = [
            (sut.RelOptionType.REL_HOME_CASE, home_and_sds_2_home_case_dir),
        ]
        for rel_option_type, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                resolver = sut.REL_OPTIONS_MAP[rel_option_type].root_resolver
                self.helper.check_under_home(resolver,
                                             rel_option_type,
                                             expected_root_path_resolver)

    def test_cwd(self):
        cases = [
            (sut.RelOptionType.REL_CWD, home_and_sds_2_cwd_dir),
        ]
        for rel_option_type, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                resolver = sut.REL_OPTIONS_MAP[rel_option_type].root_resolver
                self.helper.check_cwd(resolver,
                                      rel_option_type,
                                      expected_root_path_resolver)

    def test_dict_keys(self):
        expected = {
            sut.RelOptionType.REL_HOME_CASE,
            sut.RelOptionType.REL_ACT,
            sut.RelOptionType.REL_RESULT,
            sut.RelOptionType.REL_TMP,
            sut.RelOptionType.REL_CWD,
        }
        self.assertEqual(expected,
                         sut.REL_OPTIONS_MAP.keys())
