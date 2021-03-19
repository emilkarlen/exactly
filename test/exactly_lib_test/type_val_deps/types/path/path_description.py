import pathlib
import unittest

from exactly_lib.tcfs import relative_path_options as rpo
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_deps.types.path.impl import path_description as sut
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_part_ddv import PathPartDdv
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_tcds
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    tcds_with_act_as_curr_dir


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestPathValueWithRelativityNamePrefix)


class TestPathValueWithRelativityNamePrefix(unittest.TestCase):
    path_suffixes = [
        path_ddvs.empty_path_part(),
        path_ddvs.constant_path_part('path-suffix'),
        path_ddvs.constant_path_part('../path-suffix'),
    ]

    def test_rel_hds(self):
        tcds = fake_tcds()

        for path_suffix in self.path_suffixes:
            for rel_hds_option in rpo.RelHdsOptionType:
                with self.subTest(relativity=str(rel_hds_option),
                                  path_suffix=path_suffix.value()):
                    path_ddv = path_ddvs.rel_hds(rel_hds_option, path_suffix)
                    # ACT #
                    actual = sut.path_ddv_with_relativity_name_prefix(path_ddv,
                                                                      tcds,
                                                                      None)
                    # ASSERT #
                    expected = _expected_str(rpo.REL_HDS_OPTIONS_MAP[rel_hds_option].directory_symbol_reference,
                                             path_suffix)
                    self.assertEqual(expected, actual)

    def test_rel_sds(self):
        tcds = fake_tcds()

        for path_suffix in self.path_suffixes:
            for rel_sds_option in rpo.RelSdsOptionType:
                with self.subTest(relativity=str(rel_sds_option),
                                  path_suffix=path_suffix.value()):
                    path_ddv = path_ddvs.rel_sandbox(rel_sds_option, path_suffix)
                    # ACT #
                    actual = sut.path_ddv_with_relativity_name_prefix(path_ddv,
                                                                      tcds,
                                                                      None)
                    # ASSERT #
                    expected = _expected_str(rpo.REL_SDS_OPTIONS_MAP[rel_sds_option].directory_symbol_reference,
                                             path_suffix)
                    self.assertEqual(expected, actual)

    def test_absolute(self):
        tcds = fake_tcds()
        absolute_path = str(pathlib.Path.cwd().resolve())
        path_ddv = path_ddvs.absolute_file_name(absolute_path)
        # ACT #
        actual = sut.path_ddv_with_relativity_name_prefix(path_ddv,
                                                          tcds,
                                                          None)
        # ASSERT #
        self.assertEqual(absolute_path, actual)

    def test_cwd_that_is_under_a_test_case_dir(self):
        with tcds_with_act_as_curr_dir() as path_resolving_env:
            tcds = path_resolving_env.tcds
            for path_suffix in self.path_suffixes:
                path_ddv = path_ddvs.rel_cwd(path_suffix)

                # rel home
                for rel_hds_opt in rpo.RelHdsOptionType:
                    rel_hds_option_info = rpo.REL_HDS_OPTIONS_MAP[rel_hds_opt]
                    self._check_cwd_for_single_rel_option_type(rel_hds_option_info,
                                                               rel_hds_option_info.directory_symbol_reference,
                                                               path_suffix,
                                                               path_ddv,
                                                               tcds)

                # rel sandbox
                for rel_sds_opt in rpo.RelSdsOptionType:
                    rel_sds_option_info = rpo.REL_SDS_OPTIONS_MAP[rel_sds_opt]
                    self._check_cwd_for_single_rel_option_type(rel_sds_option_info,
                                                               rel_sds_option_info.directory_symbol_reference,
                                                               path_suffix,
                                                               path_ddv,
                                                               tcds)

    def test_cwd_that_is_under_a_non_test_case_dir_under_sandbox(self):
        # ARRANGE #
        with tcds_with_act_as_curr_dir() as path_resolving_env:
            tcds = path_resolving_env.tcds
            for path_suffix in self.path_suffixes:
                path_ddv = path_ddvs.rel_cwd(path_suffix)

                with self.subTest(path_suffix=path_suffix.value()):
                    the_cwd = tcds.sds.root_dir

                    # ACT #
                    actual = sut.path_ddv_with_relativity_name_prefix(path_ddv,
                                                                      tcds,
                                                                      the_cwd)

                    # ASSERT #

                    expected = _expected_str(sut.EXACTLY_SANDBOX_ROOT_DIR_NAME,
                                             path_suffix)

                    self.assertEqual(expected,
                                     actual)

    def _check_cwd_for_single_rel_option_type(self,
                                              expected_rel_option_info: rpo.RelOptionInfo,
                                              expected_relativity_dir_name: str,
                                              expected_path_suffix: PathPartDdv,
                                              path_ddv_to_check: PathDdv,
                                              tcds: TestCaseDs,
                                              ):
        with self.subTest(path_suffix=expected_path_suffix.value(),
                          expected_relativity_dir_name=str(expected_relativity_dir_name)):
            cwd = expected_rel_option_info.root_resolver.from_tcds(tcds).resolve()
            # ACT #
            actual = sut.path_ddv_with_relativity_name_prefix(path_ddv_to_check,
                                                              tcds,
                                                              cwd)
            # ASSERT #
            expected = _expected_str(expected_relativity_dir_name, expected_path_suffix)
            self.assertEqual(expected,
                             actual)

    def _expected_str(self, directory_name: str, path_suffix: PathPartDdv) -> str:
        return str(pathlib.PurePosixPath(directory_name, path_suffix.value()))


def _expected_str(directory_name: str, path_suffix: PathPartDdv) -> str:
    return str(pathlib.PurePosixPath(directory_name, path_suffix.value()))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
