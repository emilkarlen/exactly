import pathlib
import types
import unittest

from exactly_lib.test_case_file_structure import relativity_root
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds, fake_hds


class HdsRelativityResolverHelper:
    def __init__(self, put: unittest.TestCase):
        self.put = put
        self.hds = fake_hds()

    def check(self,
              actual_resolver,
              expected_relativity_option: relativity_root.RelHdsOptionType,
              expected_root_resolver: types.FunctionType):
        self.put.assertIsInstance(actual_resolver, relativity_root.RelHdsRootResolver)
        assert isinstance(actual_resolver, relativity_root.RelHdsRootResolver)
        expected_root = expected_root_resolver(self.hds)
        self.put.assertIs(expected_relativity_option,
                          actual_resolver.hds_relativity_type,
                          'hds_relativity_type')
        self.put.assertEqual(expected_root,
                             actual_resolver.from_hds(self.hds),
                             'from_hds')


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


class NonHdsRelativityResolverHelper:
    def __init__(self, put: unittest.TestCase):
        self.put = put
        self.sds = SandboxDirectoryStructure('sds-root')

    def check_under_sds(self,
                        actual_resolver,
                        expected_relativity_option,
                        expected_root_resolver: types.FunctionType):
        self.put.assertIsInstance(actual_resolver, relativity_root.RelNonHdsRootResolver)
        self.put.assertIs(expected_relativity_option,
                          actual_resolver.non_hds_relativity_type,
                          'relativity_type')
        self.put.assertFalse(actual_resolver.exists_pre_sds,
                             'existence pre SDS')
        expected_root = expected_root_resolver(self.sds)
        self.put.assertEqual(expected_root,
                             actual_resolver.from_sds(self.sds),
                             'from_sds')
        self.put.assertEqual(expected_root,
                             actual_resolver.from_non_hds(self.sds),
                             'from_non_hds')
        self.put.assertTrue(actual_resolver.is_rel_sds,
                            'is_rel_sds')
        self.put.assertFalse(actual_resolver.is_rel_cwd,
                             'is_rel_cwd')

    def check_cwd(self,
                  actual_resolver,
                  expected_relativity_option,
                  expected_root_resolver: types.FunctionType):
        self.put.assertIsInstance(actual_resolver, relativity_root.RelNonHdsRootResolver)
        self.put.assertIs(expected_relativity_option,
                          actual_resolver.non_hds_relativity_type,
                          'relativity_type')
        self.put.assertFalse(actual_resolver.exists_pre_sds,
                             'existence pre SDS')
        expected_root = expected_root_resolver(self.sds)
        self.put.assertEqual(expected_root,
                             actual_resolver.from_non_hds(self.sds),
                             'from_non_hds')
        self.put.assertFalse(actual_resolver.is_rel_sds,
                             'is_rel_sds')
        self.put.assertTrue(actual_resolver.is_rel_cwd,
                            'is_rel_cwd')


class AnyRelativityResolverHelper:
    def __init__(self, put: unittest.TestCase):
        self.put = put
        self.tcds = fake_tcds()
        self.sds = self.tcds.sds

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
                             actual_resolver.from_non_hds(self.sds),
                             'from_non_hds')
        self.put.assertEqual(expected_root,
                             actual_resolver.from_tcds(self.tcds),
                             'from_tcds')
        self.put.assertTrue(actual_resolver.is_rel_sds,
                            'is_rel_sds')
        self.put.assertFalse(actual_resolver.is_rel_hds,
                             'is_rel_hds')
        self.put.assertFalse(actual_resolver.is_rel_cwd,
                             'is_rel_cwd')

    def check_under_hds(self,
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
        expected_root = expected_root_resolver(self.tcds)
        self.put.assertEqual(expected_root,
                             actual_resolver.from_hds(self.tcds.hds),
                             'from_hds')
        self.put.assertEqual(expected_root,
                             actual_resolver.from_tcds(self.tcds),
                             'from_tcds')
        self.put.assertFalse(actual_resolver.is_rel_sds,
                             'is_rel_sds')
        self.put.assertTrue(actual_resolver.is_rel_hds,
                            'is_rel_hds')
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
        expected_root = expected_root_resolver(self.tcds)
        self.put.assertEqual(expected_root,
                             actual_resolver.from_non_hds(self.tcds.sds),
                             'from_non_hds')
        self.put.assertEqual(expected_root,
                             actual_resolver.from_tcds(self.tcds),
                             'from_tcds')
        self.put.assertFalse(actual_resolver.is_rel_sds,
                             'is_rel_sds')
        self.put.assertFalse(actual_resolver.is_rel_hds,
                             'is_rel_hds')
        self.put.assertTrue(actual_resolver.is_rel_cwd,
                            'is_rel_cwd')


def hds_2_hds_case_dir(hds: HomeDirectoryStructure) -> pathlib.Path:
    return hds.case_dir


def hds_2_hds_act_dir(hds: HomeDirectoryStructure) -> pathlib.Path:
    return hds.act_dir


def tcds_2_hds_case_dir(tcds: Tcds) -> pathlib.Path:
    return tcds.hds.case_dir


def tcds_2_hds_act_dir(tcds: Tcds) -> pathlib.Path:
    return tcds.hds.act_dir


def sds_2_act_dir(sds: SandboxDirectoryStructure) -> pathlib.Path:
    return sds.act_dir


def sds_2_result_dir(sds: SandboxDirectoryStructure) -> pathlib.Path:
    return sds.result.root_dir


def sds_2_tmp_user_dir(sds: SandboxDirectoryStructure) -> pathlib.Path:
    return sds.user_tmp_dir


def sds_2_cwd_dir(sds: SandboxDirectoryStructure) -> pathlib.Path:
    return pathlib.Path().cwd()


def tcds_2_cwd_dir(tcds: Tcds) -> pathlib.Path:
    return pathlib.Path().cwd()
