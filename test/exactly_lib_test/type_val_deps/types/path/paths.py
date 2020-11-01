import functools
import pathlib
import types
import unittest
from typing import Callable

from exactly_lib.tcfs import relative_path_options as rpo
from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition, RelOptionType, \
    RESOLVING_DEPENDENCY_OF, RelHdsOptionType, RelSdsOptionType
from exactly_lib.tcfs.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.type_val_deps.types.path import path_ddvs as sut
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_part_ddv import PathPartDdv
from exactly_lib.type_val_deps.types.path.path_part_ddvs import PathPartDdvAsFixedPath
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.tcfs.test_resources.paths import fake_tcds
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.test_resources.test_utils import NEA


def suite() -> unittest.TestSuite:
    configs_for_constant_rel_option_type = [
        _RelativityConfig(sut.rel_hds_case,
                          DirectoryStructurePartition.HDS,
                          lambda tcds: tcds.hds.case_dir),
        _RelativityConfig(sut.rel_hds_act,
                          DirectoryStructurePartition.HDS,
                          lambda tcds: tcds.hds.act_dir),
        _RelativityConfig(functools.partial(sut.rel_hds, RelHdsOptionType.REL_HDS_CASE),
                          DirectoryStructurePartition.HDS,
                          lambda tcds: tcds.hds.case_dir,
                          function_name='sut.rel_home(RelHomeOptionType.REL_HDS_CASE, PATH_SUFFIX)'),
        _RelativityConfig(functools.partial(sut.rel_hds, RelHdsOptionType.REL_HDS_ACT),
                          DirectoryStructurePartition.HDS,
                          lambda tcds: tcds.hds.act_dir,
                          function_name='sut.rel_home(RelHomeOptionType.REL_HDS_ACT, PATH_SUFFIX)'),
        _RelativityConfig(sut.rel_hds_act,
                          DirectoryStructurePartition.HDS,
                          lambda tcds: tcds.hds.act_dir),
        _RelativityConfig(sut.rel_tmp_user,
                          DirectoryStructurePartition.NON_HDS,
                          lambda tcds: tcds.sds.user_tmp_dir),
        _RelativityConfig(sut.rel_act,
                          DirectoryStructurePartition.NON_HDS,
                          lambda tcds: tcds.sds.act_dir),
        _RelativityConfig(sut.rel_result,
                          DirectoryStructurePartition.NON_HDS,
                          lambda tcds: tcds.sds.result.root_dir),
        _RelativityConfig(sut.rel_cwd,
                          DirectoryStructurePartition.NON_HDS,
                          lambda tcds: pathlib.Path().resolve()),
    ]
    all_configs = configs_for_constant_rel_option_type + configs_for_rel_option_argument()
    ret_val = unittest.TestSuite()
    for config in all_configs:
        ret_val.addTest(_suite_for_config(config))
    ret_val.addTest(TestDescription())
    return ret_val


def configs_for_rel_option_argument() -> list:
    ret_val = []

    for rel_option_type in RelOptionType:
        tcds_2_relativity_root = REL_OPTIONS_MAP[rel_option_type].root_resolver.from_tcds
        resolving_dependency = RESOLVING_DEPENDENCY_OF[rel_option_type]
        ret_val.append(_RelativityConfig(_of_rel_option__path_suffix_2_path(rel_option_type),
                                         resolving_dependency,
                                         tcds_2_relativity_root,
                                         function_name=sut.of_rel_option.__name__,
                                         rel_option_type_for_doc=str(rel_option_type)))
    return ret_val


def _of_rel_option__path_suffix_2_path(rel_option_type: RelOptionType) -> Callable[[PathPartDdv], PathDdv]:
    def ret_val(path_suffix: PathPartDdv) -> PathDdv:
        return sut.of_rel_option(rel_option_type, path_suffix)

    return ret_val


class _RelativityConfig:
    def __init__(self,
                 path_suffix_2_path: Callable[[PathPartDdv], PathDdv],
                 resolving_dependency: DirectoryStructurePartition,
                 tcds_2_relativity_root: types.FunctionType,
                 function_name: str = '',
                 rel_option_type_for_doc: str = ''):
        self.path_suffix_2_path = path_suffix_2_path
        self.resolving_dependency = resolving_dependency
        self.tcds_2_relativity_root = tcds_2_relativity_root
        self.function_name = function_name
        if not function_name:
            self.function_name = path_suffix_2_path.__name__
        self.rel_option_type = rel_option_type_for_doc

    @property
    def exists_pre_sds(self) -> bool:
        return self.resolving_dependency is not DirectoryStructurePartition.NON_HDS

    def __str__(self):
        return '_RelativityConfig(function_name={}, resolving_dependency={}, rel_option_type={})'.format(
            self.function_name,
            self.resolving_dependency,
            self.rel_option_type
        )


def _suite_for_config(config: _RelativityConfig) -> unittest.TestSuite:
    return unittest.TestSuite([
        TestExistsPreOrPostSds(config),
        TestDirDependencies(config),
        TestFilePath(config),
    ])


class TestForFixedRelativityBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, config: _RelativityConfig):
        super().__init__(str(config))
        self.config = config


class TestExistsPreOrPostSds(TestForFixedRelativityBase):
    def runTest(self):
        test_cases = [
            PathPartDdvAsFixedPath('file.txt'),
        ]
        for path_suffix in test_cases:
            with self.subTest():
                path = self.config.path_suffix_2_path(path_suffix)
                assert isinstance(path, PathDdv)
                self.assertEqual(self.config.exists_pre_sds,
                                 path.exists_pre_sds(),
                                 'exist pre SDS')


class TestDirDependencies(TestForFixedRelativityBase):
    def runTest(self):
        test_cases = [
            PathPartDdvAsFixedPath('file.txt'),
        ]
        for path_suffix in test_cases:
            with self.subTest():
                path = self.config.path_suffix_2_path(path_suffix)
                assert isinstance(path, PathDdv)
                self.assertEqual(True,
                                 path.has_dir_dependency(),
                                 'has_dir_dependency')
                self.assertEqual(self.config.resolving_dependency,
                                 path.resolving_dependency(),
                                 'resolving_dependency')
                if self.config.resolving_dependency is None:
                    self.assertEqual(set(),
                                     path.resolving_dependencies(),
                                     'resolving_dependencies')
                else:
                    self.assertEqual({self.config.resolving_dependency},
                                     path.resolving_dependencies(),
                                     'resolving_dependencies')


class TestFilePath(TestForFixedRelativityBase):
    def runTest(self):
        # ARRANGE #
        test_cases = [
            (PathPartDdvAsFixedPath('file.txt'),
             empty_symbol_table(),
             'file.txt'
             ),
        ]
        tcds = fake_tcds()
        for path_suffix, symbol_table, expected_path_suffix in test_cases:
            with self.subTest():
                path = self.config.path_suffix_2_path(path_suffix)
                assert isinstance(path, PathDdv)
                # ACT #
                if self.config.resolving_dependency is None:
                    tested_path_msg = 'value_when_no_dir_dependencies'
                    actual_path = path.value_when_no_dir_dependencies()

                elif self.config.exists_pre_sds:
                    tested_path_msg = 'file_path_pre_sds'
                    actual_path = path.value_pre_sds(tcds.hds)
                else:
                    tested_path_msg = 'file_path_post_sds'
                    actual_path = path.value_post_sds(tcds.sds)
                actual_path_pre_or_post_sds = path.value_of_any_dependency(tcds)
                # ASSERT #
                expected_relativity_root = self.config.tcds_2_relativity_root(tcds)
                expected_path = expected_relativity_root / expected_path_suffix
                self.assertEqual(str(expected_path),
                                 str(actual_path),
                                 tested_path_msg)
                self.assertEqual(str(expected_path),
                                 str(actual_path_pre_or_post_sds),
                                 'file_path_pre_or_post_sds')


class TestDescription(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        abs_path = pathlib.Path().resolve()
        path_part_component = 'path-part'
        cases = [
            NEA('rel-hds wo path suffix',
                expected=rpo.REL_HDS_OPTIONS_MAP[RelHdsOptionType.REL_HDS_CASE].directory_symbol_reference,
                actual=sut.of_rel_option(sut.RelOptionType.REL_HDS_CASE,
                                         sut.PathPartDdvAsNothing()),
                ),
            NEA('rel-hds w path suffix',
                expected=
                str(pathlib.Path(rpo.REL_HDS_OPTIONS_MAP[
                                     RelHdsOptionType.REL_HDS_CASE].directory_symbol_reference) / path_part_component),
                actual=sut.of_rel_option(sut.RelOptionType.REL_HDS_CASE,
                                         PathPartDdvAsFixedPath(path_part_component)),
                ),
            NEA('rel-sds',
                expected=rpo.REL_SDS_OPTIONS_MAP[RelSdsOptionType.REL_ACT].directory_symbol_reference,
                actual=sut.of_rel_option(sut.RelOptionType.REL_ACT,
                                         sut.PathPartDdvAsNothing()),
                ),
            NEA('absolute',
                expected=str(abs_path),
                actual=sut.absolute_file_name(str(abs_path)),
                ),
        ]

        for case in cases:
            with self.subTest(case.name):
                # ACT #

                actual = case.actual.describer().value.render()

                # ASSERT #

                self.assertEqual(case.expected, actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
