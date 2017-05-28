import pathlib
import unittest

from exactly_lib.test_case_file_structure import relativity_root as sut
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestAnyRelativityResolver),
    ])


class TestAnyRelativityResolver(unittest.TestCase):
    def test_under_sds(self):
        cases = [
            (sut.RelOptionType.REL_RESULT, sut.resolver_for_result, sds_2_result_dir),
            (sut.RelOptionType.REL_ACT, sut.resolver_for_act, sds_2_act_dir),
            (sut.RelOptionType.REL_TMP, sut.resolver_for_tmp_user, sds_2_tmp_user_dir),
        ]
        sds = SandboxDirectoryStructure('sds-root')
        home_and_sds = HomeAndSds(pathlib.Path('home'), sds)

        for rel_option_type, resolver, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
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
                self.assertFalse(resolver.is_rel_cwd,
                                 'is_rel_cwd')

    def test_under_home(self):
        cases = [
            (sut.RelOptionType.REL_HOME, sut.resolver_for_home, home_and_sds_2_home_dir),
        ]
        sds = SandboxDirectoryStructure('sds-root')
        home_and_sds = HomeAndSds(pathlib.Path('home'), sds)

        for rel_option_type, resolver, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                self.assertTrue(resolver.exists_pre_sds,
                                'existence pre SDS')
                expected_root = expected_root_path_resolver(home_and_sds)
                self.assertEqual(expected_root,
                                 resolver.from_home(home_and_sds.home_dir_path),
                                 'from_home')
                self.assertEqual(expected_root,
                                 resolver.from_home_and_sds(home_and_sds),
                                 'from_home_and_sds')
                self.assertFalse(resolver.is_rel_cwd,
                                 'is_rel_cwd')

    def test_cwd(self):
        cases = [
            (sut.RelOptionType.REL_CWD, sut.resolver_for_cwd, home_and_sds_2_cwd_dir),
        ]
        sds = SandboxDirectoryStructure('sds-root')
        home_and_sds = HomeAndSds(pathlib.Path('home'), sds)

        for rel_option_type, resolver, expected_root_path_resolver in cases:
            with self.subTest(msg=str(rel_option_type)):
                self.assertFalse(resolver.exists_pre_sds,
                                 'existence pre SDS')
                expected_root = expected_root_path_resolver(home_and_sds)
                self.assertEqual(expected_root,
                                 resolver.from_home_and_sds(home_and_sds),
                                 'from_home_and_sds')
                self.assertTrue(resolver.is_rel_cwd,
                                'is_rel_cwd')


def sds_2_act_dir(sds: SandboxDirectoryStructure) -> pathlib.Path:
    return sds.act_dir


def sds_2_result_dir(sds: SandboxDirectoryStructure) -> pathlib.Path:
    return sds.result.root_dir


def sds_2_tmp_user_dir(sds: SandboxDirectoryStructure) -> pathlib.Path:
    return sds.tmp.user_dir


def home_and_sds_2_home_dir(home_and_sds: HomeAndSds) -> pathlib.Path:
    return home_and_sds.home_dir_path


def home_and_sds_2_cwd_dir(home_and_sds: HomeAndSds) -> pathlib.Path:
    return pathlib.Path().resolve()
