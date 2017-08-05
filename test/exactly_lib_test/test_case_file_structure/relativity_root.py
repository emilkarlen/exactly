import unittest

from exactly_lib.test_case_file_structure import relativity_root as sut
from exactly_lib_test.test_case_file_structure.test_resources import relativity_test_utils as utils
from exactly_lib_test.test_case_file_structure.test_resources.relativity_test_utils import sds_2_act_dir, \
    sds_2_result_dir, sds_2_tmp_user_dir, home_and_sds_2_home_case_dir, home_and_sds_2_cwd_dir


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSdsRelativityResolver),
        unittest.makeSuite(TestNonHomeRelativityResolver),
        unittest.makeSuite(TestAnyRelativityResolver),
    ])


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


class TestNonHomeRelativityResolver(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName)
        self.helper = utils.NonHomeRelativityResolverHelper(self)

    def test_under_sds(self):
        cases = [
            (sut.RelNonHomeOptionType.REL_RESULT, sut.resolver_for_result, sds_2_result_dir),
            (sut.RelNonHomeOptionType.REL_ACT, sut.resolver_for_act, sds_2_act_dir),
            (sut.RelNonHomeOptionType.REL_TMP, sut.resolver_for_tmp_user, sds_2_tmp_user_dir),
        ]
        for rel_option_type, resolver, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                self.helper.check_under_sds(resolver,
                                            rel_option_type,
                                            expected_root_path_resolver)

    def test_cwd(self):
        cases = [
            (sut.RelNonHomeOptionType.REL_CWD, sut.resolver_for_cwd, home_and_sds_2_cwd_dir),
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

    def test_under_home(self):
        cases = [
            (sut.RelOptionType.REL_HOME, sut.resolver_for_home, home_and_sds_2_home_case_dir),
        ]
        for rel_option_type, resolver, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                self.helper.check_under_home(resolver,
                                             rel_option_type,
                                             expected_root_path_resolver)

    def test_cwd(self):
        cases = [
            (sut.RelOptionType.REL_CWD, sut.resolver_for_cwd, home_and_sds_2_cwd_dir),
        ]
        for rel_option_type, resolver, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                self.helper.check_cwd(resolver,
                                      rel_option_type,
                                      expected_root_path_resolver)
