import pathlib
import unittest

from exactly_lib.test_case_file_structure import relative_path_options as rpo
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.err_msg import path_description as sut
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsFixedPath, PathPartAsNothing
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.path_part import PathPart
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_home_and_sds
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    path_suffixes = [
        PathPartAsNothing(),
        PathPartAsFixedPath('path-suffix'),
        PathPartAsFixedPath('../path-suffix'),
    ]

    def test_rel_home(self):
        home_and_sds = fake_home_and_sds()

        for path_suffix in self.path_suffixes:
            for rel_home_option in rpo.RelHomeOptionType:
                with self.subTest(relativity=str(rel_home_option),
                                  path_suffix=path_suffix.value()):
                    path_value = file_refs.rel_home(rel_home_option, path_suffix)
                    # ACT #
                    actual = sut.path_value_with_relativity_name_prefix(path_value, home_and_sds,
                                                                        pathlib.Path.cwd())
                    # ASSERT #
                    expected = self._expected_str(rpo.REL_HOME_OPTIONS_MAP[rel_home_option].directory_name,
                                                  path_suffix)
                    self.assertEqual(expected, actual)

    def test_rel_sds(self):
        home_and_sds = fake_home_and_sds()

        for path_suffix in self.path_suffixes:
            for rel_sds_option in rpo.RelSdsOptionType:
                with self.subTest(relativity=str(rel_sds_option),
                                  path_suffix=path_suffix.value()):
                    path_value = file_refs.rel_sandbox(rel_sds_option, path_suffix)
                    # ACT #
                    actual = sut.path_value_with_relativity_name_prefix(path_value, home_and_sds,
                                                                        pathlib.Path.cwd())
                    # ASSERT #
                    expected = self._expected_str(rpo.REL_SDS_OPTIONS_MAP[rel_sds_option].directory_name,
                                                  path_suffix)
                    self.assertEqual(expected, actual)

    def test_absolute(self):
        home_and_sds = fake_home_and_sds()
        absolute_path = str(pathlib.Path.cwd().resolve())
        path_value = file_refs.absolute_file_name(absolute_path)
        # ACT #
        actual = sut.path_value_with_relativity_name_prefix(path_value, home_and_sds,
                                                            pathlib.Path.cwd())
        # ASSERT #
        self.assertEqual(absolute_path, actual)

    def test_cwd_that_is_under_a_test_case_dir(self):
        with home_and_sds_with_act_as_curr_dir() as path_resolving_env:
            home_and_sds = path_resolving_env.home_and_sds
            for path_suffix in self.path_suffixes:
                path_value = file_refs.rel_cwd(path_suffix)

                # rel home
                for rel_home_opt in rpo.RelHomeOptionType:
                    rel_home_option_info = rpo.REL_HOME_OPTIONS_MAP[rel_home_opt]
                    self._check_cwd_for_single_rel_option_type(rel_home_option_info,
                                                               rel_home_option_info.directory_name,
                                                               path_suffix,
                                                               path_value,
                                                               home_and_sds)

                # rel sandbox
                for rel_sds_opt in rpo.RelSdsOptionType:
                    rel_sds_option_info = rpo.REL_SDS_OPTIONS_MAP[rel_sds_opt]
                    self._check_cwd_for_single_rel_option_type(rel_sds_option_info,
                                                               rel_sds_option_info.directory_name,
                                                               path_suffix,
                                                               path_value,
                                                               home_and_sds)

    def test_cwd_that_is_under_a_non_test_case_dir_under_sandbox(self):
        # ARRANGE #
        with home_and_sds_with_act_as_curr_dir() as path_resolving_env:
            home_and_sds = path_resolving_env.home_and_sds
            for path_suffix in self.path_suffixes:
                path_value = file_refs.rel_cwd(path_suffix)

                with self.subTest(path_suffix=path_suffix.value()):
                    the_cwd = home_and_sds.sds.root_dir

                    # ACT #
                    actual = sut.path_value_with_relativity_name_prefix(path_value,
                                                                        home_and_sds,
                                                                        the_cwd)

                    # ASSERT #

                    expected = self._expected_str(sut.EXACTLY_SANDBOX_ROOT_DIR_NAME,
                                                  path_suffix)

                    self.assertEqual(expected,
                                     actual)

    def _check_cwd_for_single_rel_option_type(self,
                                              expected_rel_option_info: rpo.RelOptionInfo,
                                              expected_relativity_dir_name: str,
                                              expected_path_suffix: PathPart,
                                              path_value_to_check: FileRef,
                                              home_and_sds: HomeAndSds,
                                              ):
        with self.subTest(path_suffix=expected_path_suffix.value(),
                          expected_relativity_dir_name=str(expected_relativity_dir_name)):
            cwd = expected_rel_option_info.root_resolver.from_home_and_sds(home_and_sds).resolve()
            # ACT #
            actual = sut.path_value_with_relativity_name_prefix(path_value_to_check, home_and_sds,
                                                                cwd)
            # ASSERT #
            expected = self._expected_str(expected_relativity_dir_name, expected_path_suffix)
            self.assertEqual(expected,
                             actual)

    def _expected_str(self, directory_name: str, path_suffix: PathPart) -> str:
        return str(pathlib.PosixPath(directory_name, path_suffix.value()))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
