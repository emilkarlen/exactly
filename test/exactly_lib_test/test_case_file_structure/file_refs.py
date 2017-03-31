import pathlib
import unittest

import types

from exactly_lib.test_case_file_structure import file_refs as sut
from exactly_lib.test_case_file_structure import sandbox_directory_structure as _sds
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
                 file_name_2_file_ref: types.FunctionType,
                 exists_pre_sds: bool,
                 home_and_sds_2_relativity_root: types.FunctionType):
        self.file_name_2_file_ref = file_name_2_file_ref
        self.exists_pre_sds = exists_pre_sds
        self.home_and_sds_2_relativity_root = home_and_sds_2_relativity_root


def _suite_for_config(config: _RelativityConfig) -> unittest.TestSuite:
    return unittest.TestSuite([
        TestShouldReferenceNoValueDefinitions(config),
        TestExistsPreOrPostSds(config),
        TestFilePath(config),
        TestFilePathPreOrPostSds(config),
    ])


class TestForFixedRelativityBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, config: _RelativityConfig):
        super().__init__(config)
        self.config = config


class TestShouldReferenceNoValueDefinitions(TestForFixedRelativityBase):
    def runTest(self):
        file_reference = self.config.file_name_2_file_ref('file.txt')
        self.assertTrue(len(file_reference.value_references_of_paths()) == 0,
                        'File is expected to reference no variable definitions')


class TestExistsPreOrPostSds(TestForFixedRelativityBase):
    def runTest(self):
        file_reference = self.config.file_name_2_file_ref('file.txt')
        self.assertEquals(self.config.exists_pre_sds,
                          file_reference.exists_pre_sds(empty_symbol_table()),
                          'exist pre SDS')


class TestFilePath(TestForFixedRelativityBase):
    def runTest(self):
        file_name = 'file.txt'
        file_reference = self.config.file_name_2_file_ref(file_name)
        assert isinstance(file_reference, FileRef)
        home_and_sds = _home_and_sds()
        environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds, empty_symbol_table())
        if self.config.exists_pre_sds:
            actual_path = file_reference.file_path_pre_sds(environment)
        else:
            actual_path = file_reference.file_path_post_sds(environment)
        expected_relativity_root = self.config.home_and_sds_2_relativity_root(home_and_sds)
        expected_path = expected_relativity_root / file_name
        self.assertEquals(str(expected_path),
                          str(actual_path),
                          'file_path')


class TestFilePathPreOrPostSds(TestForFixedRelativityBase):
    def runTest(self):
        file_reference = self.config.file_name_2_file_ref('file.txt')
        assert isinstance(file_reference, FileRef)
        home_and_sds = _home_and_sds()
        environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds, empty_symbol_table())
        actual_path = file_reference.file_path_pre_or_post_sds(environment)
        expected_relativity_root = self.config.home_and_sds_2_relativity_root(home_and_sds)
        expected_path = expected_relativity_root / 'file.txt'
        self.assertEquals(str(expected_path),
                          str(actual_path),
                          'file_path')


def _home_and_sds() -> HomeAndSds:
    return HomeAndSds(pathlib.Path('home'),
                      _sds.SandboxDirectoryStructure('sds'))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
