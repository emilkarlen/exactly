import pathlib
import types
import unittest

from exactly_lib.test_case_file_structure import relativity_root
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


class SdsRelativityResolverHelper:
    def __init__(self, put: unittest.TestCase):
        self.put = put
        self.sds = SandboxDirectoryStructure('sds-root')

    def check(self,
              actual_resolver,
              expected_relativity_option,
              expected_root_resolver: types.FunctionType):
        self.put.assertIsInstance(actual_resolver, relativity_root.RelSdsRootResolver)
        assert isinstance(actual_resolver, relativity_root.RelSdsRootResolver)
        expected_root = expected_root_resolver(self.sds)
        self.put.assertIs(expected_relativity_option,
                          actual_resolver.sds_relativity_type,
                          'sds_relativity_type')
        self.put.assertEqual(expected_root,
                             actual_resolver.from_sds(self.sds),
                             'from_sds')


class NonHomeRelativityResolverHelper:
    def __init__(self, put: unittest.TestCase):
        self.put = put
        self.sds = SandboxDirectoryStructure('sds-root')

    def check_under_sds(self,
                        actual_resolver,
                        expected_relativity_option,
                        expected_root_resolver: types.FunctionType):
        self.put.assertIsInstance(actual_resolver, relativity_root.RelNonHomeRootResolver)
        self.put.assertIs(expected_relativity_option,
                          actual_resolver.non_home_relativity_type,
                          'relativity_type')
        self.put.assertFalse(actual_resolver.exists_pre_sds,
                             'existence pre SDS')
        expected_root = expected_root_resolver(self.sds)
        self.put.assertEqual(expected_root,
                             actual_resolver.from_sds(self.sds),
                             'from_sds')
        self.put.assertEqual(expected_root,
                             actual_resolver.from_non_home(self.sds),
                             'from_non_home')
        self.put.assertTrue(actual_resolver.is_rel_sds,
                            'is_rel_sds')
        self.put.assertFalse(actual_resolver.is_rel_cwd,
                             'is_rel_cwd')

    def check_cwd(self,
                  actual_resolver,
                  expected_relativity_option,
                  expected_root_resolver: types.FunctionType):
        self.put.assertIsInstance(actual_resolver, relativity_root.RelNonHomeRootResolver)
        self.put.assertIs(expected_relativity_option,
                          actual_resolver.non_home_relativity_type,
                          'relativity_type')
        self.put.assertFalse(actual_resolver.exists_pre_sds,
                             'existence pre SDS')
        expected_root = expected_root_resolver(self.sds)
        self.put.assertEqual(expected_root,
                             actual_resolver.from_non_home(self.sds),
                             'from_non_home')
        self.put.assertFalse(actual_resolver.is_rel_sds,
                             'is_rel_sds')
        self.put.assertTrue(actual_resolver.is_rel_cwd,
                            'is_rel_cwd')


class AnyRelativityResolverHelper:
    def __init__(self, put: unittest.TestCase):
        self.put = put
        self.sds = SandboxDirectoryStructure('sds-root')
        self.home_and_sds = HomeAndSds(pathlib.Path('home'), self.sds)

    def check_under_sds(self,
                        actual_resolver,
                        expected_relativity_option,
                        expected_root_resolver: types.FunctionType):
        self.put.assertIsInstance(actual_resolver,
                                  relativity_root.RelRootResolver)
        self.put.assertIs(expected_relativity_option,
                          actual_resolver.relativity_type,
                          'relativity_type')
        self.put.assertFalse(actual_resolver.exists_pre_sds,
                             'existence pre SDS')
        expected_root = expected_root_resolver(self.sds)
        self.put.assertEqual(expected_root,
                             actual_resolver.from_sds(self.sds),
                             'from_sds')
        self.put.assertEqual(expected_root,
                             actual_resolver.from_non_home(self.sds),
                             'from_non_home')
        self.put.assertEqual(expected_root,
                             actual_resolver.from_home_and_sds(self.home_and_sds),
                             'from_home_and_sds')
        self.put.assertTrue(actual_resolver.is_rel_sds,
                            'is_rel_sds')
        self.put.assertFalse(actual_resolver.is_rel_home,
                             'is_rel_home')
        self.put.assertFalse(actual_resolver.is_rel_cwd,
                             'is_rel_cwd')

    def check_under_home(self,
                         actual_resolver,
                         expected_relativity_option,
                         expected_root_resolver: types.FunctionType):
        self.put.assertIsInstance(actual_resolver,
                                  relativity_root.RelRootResolver)
        self.put.assertIs(expected_relativity_option,
                          actual_resolver.relativity_type,
                          'relativity_type')
        self.put.assertTrue(actual_resolver.exists_pre_sds,
                            'existence pre SDS')
        expected_root = expected_root_resolver(self.home_and_sds)
        self.put.assertEqual(expected_root,
                             actual_resolver.from_home(self.home_and_sds.home_dir_path),
                             'from_home')
        self.put.assertEqual(expected_root,
                             actual_resolver.from_home_and_sds(self.home_and_sds),
                             'from_home_and_sds')
        self.put.assertFalse(actual_resolver.is_rel_sds,
                             'is_rel_sds')
        self.put.assertTrue(actual_resolver.is_rel_home,
                            'is_rel_home')
        self.put.assertFalse(actual_resolver.is_rel_cwd,
                             'is_rel_cwd')

    def check_cwd(self,
                  actual_resolver,
                  expected_relativity_option,
                  expected_root_resolver: types.FunctionType):
        self.put.assertIsInstance(actual_resolver,
                                  relativity_root.RelRootResolver)
        self.put.assertIs(expected_relativity_option,
                          actual_resolver.relativity_type,
                          'relativity_type')
        self.put.assertFalse(actual_resolver.exists_pre_sds,
                             'existence pre SDS')
        expected_root = expected_root_resolver(self.home_and_sds)
        self.put.assertEqual(expected_root,
                             actual_resolver.from_non_home(self.home_and_sds.sds),
                             'from_non_home')
        self.put.assertEqual(expected_root,
                             actual_resolver.from_home_and_sds(self.home_and_sds),
                             'from_home_and_sds')
        self.put.assertFalse(actual_resolver.is_rel_sds,
                             'is_rel_sds')
        self.put.assertFalse(actual_resolver.is_rel_home,
                             'is_rel_home')
        self.put.assertTrue(actual_resolver.is_rel_cwd,
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
