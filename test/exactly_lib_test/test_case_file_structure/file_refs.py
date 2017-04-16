import pathlib
import unittest

import types

from exactly_lib.test_case_file_structure import file_refs as sut
from exactly_lib.test_case_file_structure import sandbox_directory_structure as _sds
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType


def suite() -> unittest.TestSuite:
    configs = [
        _RelativityConfig(sut.rel_home,
                          True,
                          lambda home_and_sds: home_and_sds.home_dir_path),
        _RelativityConfig(sut.rel_tmp_user,
                          False,
                          lambda home_and_sds: home_and_sds.sds.tmp.user_dir),
        _RelativityConfig(sut.rel_act,
                          False,
                          lambda home_and_sds: home_and_sds.sds.act_dir),
        _RelativityConfig(sut.rel_result,
                          False,
                          lambda home_and_sds: home_and_sds.sds.result.root_dir),
        _RelativityConfig(sut.rel_cwd,
                          False,
                          lambda home_and_sds: pathlib.Path().resolve()),
    ]

    ret_val = unittest.TestSuite()
    for config in configs:
        ret_val.addTest(_suite_for_config(config))
    return ret_val


class _RelativityConfig:
    def __init__(self,
                 path_suffix_2_file_ref: types.FunctionType,
                 exists_pre_sds: bool,
                 home_and_sds_2_relativity_root: types.FunctionType):
        self.path_suffix_2_file_ref = path_suffix_2_file_ref
        self.exists_pre_sds = exists_pre_sds
        self.home_and_sds_2_relativity_root = home_and_sds_2_relativity_root


def _suite_for_config(config: _RelativityConfig) -> unittest.TestSuite:
    return unittest.TestSuite([
        TestExistsPreOrPostSds(config),
        TestFilePath(config),
    ])


class TestForFixedRelativityBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, config: _RelativityConfig):
        super().__init__(config)
        self.config = config


class TestExistsPreOrPostSds(TestForFixedRelativityBase):
    def runTest(self):
        test_cases = [
            PathPartAsFixedPath('file.txt'),
        ]
        for path_suffix in test_cases:
            with self.subTest():
                file_reference = self.config.path_suffix_2_file_ref(path_suffix)
                self.assertEqual(self.config.exists_pre_sds,
                                 file_reference.exists_pre_sds(empty_symbol_table()),
                                 'exist pre SDS')


class TestFilePath(TestForFixedRelativityBase):
    def runTest(self):
        # ARRANGE #
        test_cases = [
            (PathPartAsFixedPath('file.txt'),
             empty_symbol_table(),
             'file.txt'
             ),
        ]
        home_and_sds = _home_and_sds()
        for path_suffix, symbol_table, expected_path_suffix in test_cases:
            with self.subTest():
                file_reference = self.config.path_suffix_2_file_ref(path_suffix)
                assert isinstance(file_reference, FileRef)
                environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds, symbol_table)
                # ACT #
                if self.config.exists_pre_sds:
                    tested_path_msg = 'file_path_pre_sds'
                    actual_path = file_reference.file_path_pre_sds(environment)
                else:
                    tested_path_msg = 'file_path_post_sds'
                    actual_path = file_reference.file_path_post_sds(environment)
                actual_path_pre_or_post_sds = file_reference.file_path_pre_or_post_sds(environment)
                # ASSERT #
                expected_relativity_root = self.config.home_and_sds_2_relativity_root(home_and_sds)
                expected_path = expected_relativity_root / expected_path_suffix
                self.assertEqual(str(expected_path),
                                 str(actual_path),
                                 tested_path_msg)
                self.assertEqual(str(expected_path),
                                 str(actual_path_pre_or_post_sds),
                                 'file_path_pre_or_post_sds')


def _home_and_sds() -> HomeAndSds:
    return HomeAndSds(pathlib.Path('home'),
                      _sds.SandboxDirectoryStructure('sds'))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
