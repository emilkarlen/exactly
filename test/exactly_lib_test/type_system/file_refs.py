import functools
import pathlib
import types
import unittest

from exactly_lib.test_case_file_structure.path_relativity import ResolvingDependency, RelOptionType, \
    RESOLVING_DEPENDENCY_OF, RelHomeOptionType
from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.type_system import file_refs as sut
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.path_part import PathPart
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_home_and_sds
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType


def suite() -> unittest.TestSuite:
    configs_for_constant_rel_option_type = [
        _RelativityConfig(sut.rel_home_case,
                          ResolvingDependency.HOME,
                          lambda home_and_sds: home_and_sds.hds.case_dir),
        _RelativityConfig(sut.rel_home_act,
                          ResolvingDependency.HOME,
                          lambda home_and_sds: home_and_sds.hds.act_dir),
        _RelativityConfig(functools.partial(sut.rel_home, RelHomeOptionType.REL_HOME_CASE),
                          ResolvingDependency.HOME,
                          lambda home_and_sds: home_and_sds.hds.case_dir,
                          function_name='sut.rel_home(RelHomeOptionType.REL_HOME_CASE, PATH_SUFFIX)'),
        _RelativityConfig(functools.partial(sut.rel_home, RelHomeOptionType.REL_HOME_ACT),
                          ResolvingDependency.HOME,
                          lambda home_and_sds: home_and_sds.hds.act_dir,
                          function_name='sut.rel_home(RelHomeOptionType.REL_HOME_ACT, PATH_SUFFIX)'),
        _RelativityConfig(sut.rel_home_act,
                          ResolvingDependency.HOME,
                          lambda home_and_sds: home_and_sds.hds.act_dir),
        _RelativityConfig(sut.rel_tmp_user,
                          ResolvingDependency.NON_HOME,
                          lambda home_and_sds: home_and_sds.sds.tmp.user_dir),
        _RelativityConfig(sut.rel_act,
                          ResolvingDependency.NON_HOME,
                          lambda home_and_sds: home_and_sds.sds.act_dir),
        _RelativityConfig(sut.rel_result,
                          ResolvingDependency.NON_HOME,
                          lambda home_and_sds: home_and_sds.sds.result.root_dir),
        _RelativityConfig(sut.rel_cwd,
                          ResolvingDependency.NON_HOME,
                          lambda home_and_sds: pathlib.Path().resolve()),
    ]
    all_configs = configs_for_constant_rel_option_type + configs_for_rel_option_argument()
    ret_val = unittest.TestSuite()
    for config in all_configs:
        ret_val.addTest(_suite_for_config(config))
    return ret_val


def configs_for_rel_option_argument() -> list:
    ret_val = []

    for rel_option_type in RelOptionType:
        home_and_sds_2_relativity_root = REL_OPTIONS_MAP[rel_option_type].root_resolver.from_home_and_sds
        resolving_dependency = RESOLVING_DEPENDENCY_OF[rel_option_type]
        ret_val.append(_RelativityConfig(_of_rel_option__path_suffix_2_file_ref(rel_option_type),
                                         resolving_dependency,
                                         home_and_sds_2_relativity_root,
                                         function_name=sut.of_rel_option.__name__,
                                         rel_option_type_for_doc=str(rel_option_type)))
    return ret_val


def _of_rel_option__path_suffix_2_file_ref(rel_option_type: RelOptionType) -> types.FunctionType:
    def ret_val(path_suffix: PathPart) -> FileRef:
        return sut.of_rel_option(rel_option_type, path_suffix)

    return ret_val


class _RelativityConfig:
    def __init__(self,
                 path_suffix_2_file_ref: types.FunctionType,
                 resolving_dependency: ResolvingDependency,
                 home_and_sds_2_relativity_root: types.FunctionType,
                 function_name: str = '',
                 rel_option_type_for_doc: str = ''):
        self.path_suffix_2_file_ref = path_suffix_2_file_ref
        self.resolving_dependency = resolving_dependency
        self.home_and_sds_2_relativity_root = home_and_sds_2_relativity_root
        self.function_name = function_name
        if not function_name:
            self.function_name = path_suffix_2_file_ref.__name__
        self.rel_option_type = rel_option_type_for_doc

    @property
    def exists_pre_sds(self) -> bool:
        return self.resolving_dependency is not ResolvingDependency.NON_HOME

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
            PathPartAsFixedPath('file.txt'),
        ]
        for path_suffix in test_cases:
            with self.subTest():
                file_reference = self.config.path_suffix_2_file_ref(path_suffix)
                assert isinstance(file_reference, FileRef)
                self.assertEqual(self.config.exists_pre_sds,
                                 file_reference.exists_pre_sds(),
                                 'exist pre SDS')


class TestDirDependencies(TestForFixedRelativityBase):
    def runTest(self):
        test_cases = [
            PathPartAsFixedPath('file.txt'),
        ]
        for path_suffix in test_cases:
            with self.subTest():
                file_reference = self.config.path_suffix_2_file_ref(path_suffix)
                assert isinstance(file_reference, FileRef)
                self.assertEqual(True,
                                 file_reference.has_dir_dependency(),
                                 'has_dir_dependency')
                self.assertEqual(self.config.resolving_dependency,
                                 file_reference.resolving_dependency(),
                                 'resolving_dependency')
                if self.config.resolving_dependency is None:
                    self.assertEqual(set(),
                                     file_reference.resolving_dependencies(),
                                     'resolving_dependencies')
                else:
                    self.assertEqual({self.config.resolving_dependency},
                                     file_reference.resolving_dependencies(),
                                     'resolving_dependencies')


class TestFilePath(TestForFixedRelativityBase):
    def runTest(self):
        # ARRANGE #
        test_cases = [
            (PathPartAsFixedPath('file.txt'),
             empty_symbol_table(),
             'file.txt'
             ),
        ]
        home_and_sds = fake_home_and_sds()
        for path_suffix, symbol_table, expected_path_suffix in test_cases:
            with self.subTest():
                file_reference = self.config.path_suffix_2_file_ref(path_suffix)
                assert isinstance(file_reference, FileRef)
                # ACT #
                if self.config.resolving_dependency is None:
                    tested_path_msg = 'value_when_no_dir_dependencies'
                    actual_path = file_reference.value_when_no_dir_dependencies()

                elif self.config.exists_pre_sds:
                    tested_path_msg = 'file_path_pre_sds'
                    actual_path = file_reference.value_pre_sds(home_and_sds.hds)
                else:
                    tested_path_msg = 'file_path_post_sds'
                    actual_path = file_reference.value_post_sds(home_and_sds.sds)
                actual_path_pre_or_post_sds = file_reference.value_of_any_dependency(home_and_sds)
                # ASSERT #
                expected_relativity_root = self.config.home_and_sds_2_relativity_root(home_and_sds)
                expected_path = expected_relativity_root / expected_path_suffix
                self.assertEqual(str(expected_path),
                                 str(actual_path),
                                 tested_path_msg)
                self.assertEqual(str(expected_path),
                                 str(actual_path_pre_or_post_sds),
                                 'file_path_pre_or_post_sds')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
