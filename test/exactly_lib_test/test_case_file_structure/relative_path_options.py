import pathlib
import unittest

from exactly_lib.test_case_file_structure import relative_path_options as sut
from exactly_lib.test_case_file_structure import relativity_root
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSdsRelativityResolver),
        unittest.makeSuite(TestNonHomeRelativityResolver),
        unittest.makeSuite(TestAnyRelativityResolver),
    ])


class TestSdsRelativityResolver(unittest.TestCase):
    def _resolver(self, relativity: sut.RelSdsOptionType) -> relativity_root.RelSdsRootResolver:
        ret_val = sut.REL_SDS_OPTIONS_MAP[relativity].root_resolver
        self.assertIsInstance(ret_val, relativity_root.RelSdsRootResolver)
        return ret_val

    def test(self):
        cases = [
            (sut.RelSdsOptionType.REL_RESULT, sds_2_result_dir),
            (sut.RelSdsOptionType.REL_ACT, sds_2_act_dir),
            (sut.RelSdsOptionType.REL_TMP, sds_2_tmp_user_dir),
        ]
        sds = SandboxDirectoryStructure('sds-root')

        for rel_option_type, expected_root_path_resolver in cases:
            resolver = self._resolver(rel_option_type)
            with self.subTest(msg=str(rel_option_type)):
                expected_root = expected_root_path_resolver(sds)
                self.assertIs(rel_option_type,
                              resolver.sds_relativity_type,
                              'relativity_type')
                self.assertEqual(expected_root,
                                 resolver.from_sds(sds),
                                 'from_sds')


class TestNonHomeRelativityResolver(unittest.TestCase):
    def _resolver(self, relativity: sut.RelNonHomeOptionType) -> relativity_root.RelNonHomeRootResolver:
        ret_val = sut.REL_NON_HOME_OPTIONS_MAP[relativity].root_resolver
        self.assertIsInstance(ret_val, relativity_root.RelNonHomeRootResolver)
        return ret_val

    def test_under_sds(self):
        cases = [
            (sut.RelNonHomeOptionType.REL_RESULT, sds_2_result_dir),
            (sut.RelNonHomeOptionType.REL_ACT, sds_2_act_dir),
            (sut.RelNonHomeOptionType.REL_TMP, sds_2_tmp_user_dir),
        ]
        sds = SandboxDirectoryStructure('sds-root')

        for rel_option_type, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                resolver = self._resolver(rel_option_type)
                self.assertIs(rel_option_type,
                              resolver.non_home_relativity_type,
                              'relativity_type')
                self.assertFalse(resolver.exists_pre_sds,
                                 'existence pre SDS')
                expected_root = expected_root_path_resolver(sds)
                self.assertEqual(expected_root,
                                 resolver.from_sds(sds),
                                 'from_sds')
                self.assertEqual(expected_root,
                                 resolver.from_non_home(sds),
                                 'from_non_home')
                self.assertTrue(resolver.is_rel_sds,
                                'is_rel_sds')
                self.assertFalse(resolver.is_rel_cwd,
                                 'is_rel_cwd')

    def test_cwd(self):
        cases = [
            (sut.RelNonHomeOptionType.REL_CWD, home_and_sds_2_cwd_dir),
        ]
        sds = SandboxDirectoryStructure('sds-root')

        for rel_option_type, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                resolver = self._resolver(rel_option_type)
                self.assertIs(rel_option_type,
                              resolver.non_home_relativity_type,
                              'relativity_type')
                self.assertFalse(resolver.exists_pre_sds,
                                 'existence pre SDS')
                expected_root = expected_root_path_resolver(sds)
                self.assertEqual(expected_root,
                                 resolver.from_non_home(sds),
                                 'from_non_home')
                self.assertFalse(resolver.is_rel_sds,
                                 'is_rel_sds')
                self.assertTrue(resolver.is_rel_cwd,
                                'is_rel_cwd')


class TestAnyRelativityResolver(unittest.TestCase):
    def _resolver(self, relativity: sut.RelOptionType) -> relativity_root.RelRootResolver:
        ret_val = sut.REL_OPTIONS_MAP[relativity].root_resolver
        self.assertIsInstance(ret_val, relativity_root.RelRootResolver)
        return ret_val

    def test_under_sds(self):
        cases = [
            (sut.RelOptionType.REL_RESULT, sds_2_result_dir),
            (sut.RelOptionType.REL_ACT, sds_2_act_dir),
            (sut.RelOptionType.REL_TMP, sds_2_tmp_user_dir),
        ]
        sds = SandboxDirectoryStructure('sds-root')
        home_and_sds = HomeAndSds(pathlib.Path('home'), sds)

        for rel_option_type, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                resolver = self._resolver(rel_option_type)
                self.assertIs(rel_option_type,
                              resolver.relativity_type,
                              'relativity_type')
                self.assertFalse(resolver.exists_pre_sds,
                                 'existence pre SDS')
                expected_root = expected_root_path_resolver(sds)
                self.assertEqual(expected_root,
                                 resolver.from_sds(sds),
                                 'from_sds')
                self.assertEqual(expected_root,
                                 resolver.from_non_home(sds),
                                 'from_non_home')
                self.assertEqual(expected_root,
                                 resolver.from_home_and_sds(home_and_sds),
                                 'from_home_and_sds')
                self.assertTrue(resolver.is_rel_sds,
                                'is_rel_sds')
                self.assertFalse(resolver.is_rel_home,
                                 'is_rel_home')
                self.assertFalse(resolver.is_rel_cwd,
                                 'is_rel_cwd')

    def test_under_home(self):
        cases = [
            (sut.RelOptionType.REL_HOME, home_and_sds_2_home_dir),
        ]
        sds = SandboxDirectoryStructure('sds-root')
        home_and_sds = HomeAndSds(pathlib.Path('home'), sds)

        for rel_option_type, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                resolver = self._resolver(rel_option_type)
                self.assertTrue(resolver.exists_pre_sds,
                                'existence pre SDS')
                expected_root = expected_root_path_resolver(home_and_sds)
                self.assertEqual(expected_root,
                                 resolver.from_home(home_and_sds.home_dir_path),
                                 'from_home')
                self.assertEqual(expected_root,
                                 resolver.from_home_and_sds(home_and_sds),
                                 'from_home_and_sds')
                self.assertFalse(resolver.is_rel_sds,
                                 'is_rel_sds')
                self.assertTrue(resolver.is_rel_home,
                                'is_rel_home')
                self.assertFalse(resolver.is_rel_cwd,
                                 'is_rel_cwd')

    def test_cwd(self):
        cases = [
            (sut.RelOptionType.REL_CWD, home_and_sds_2_cwd_dir),
        ]
        sds = SandboxDirectoryStructure('sds-root')
        home_and_sds = HomeAndSds(pathlib.Path('home'), sds)

        for rel_option_type, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                resolver = self._resolver(rel_option_type)
                self.assertFalse(resolver.exists_pre_sds,
                                 'existence pre SDS')
                expected_root = expected_root_path_resolver(home_and_sds)
                self.assertEqual(expected_root,
                                 resolver.from_non_home(sds),
                                 'from_non_home')
                self.assertEqual(expected_root,
                                 resolver.from_home_and_sds(home_and_sds),
                                 'from_home_and_sds')
                self.assertFalse(resolver.is_rel_sds,
                                 'is_rel_sds')
                self.assertFalse(resolver.is_rel_home,
                                 'is_rel_home')
                self.assertTrue(resolver.is_rel_cwd,
                                'is_rel_cwd')


def sds_2_act_dir(sds: SandboxDirectoryStructure) -> pathlib.Path:
    return sds.act_dir


def sds_2_result_dir(sds: SandboxDirectoryStructure) -> pathlib.Path:
    return sds.result.root_dir


def sds_2_tmp_user_dir(sds: SandboxDirectoryStructure) -> pathlib.Path:
    return sds.tmp.user_dir


def sds_2_cwd_dir(sds: SandboxDirectoryStructure) -> pathlib.Path:
    return pathlib.Path().cwd()


def home_and_sds_2_home_dir(home_and_sds: HomeAndSds) -> pathlib.Path:
    return home_and_sds.home_dir_path


def home_and_sds_2_cwd_dir(home_and_sds: HomeAndSds) -> pathlib.Path:
    return pathlib.Path().cwd()
