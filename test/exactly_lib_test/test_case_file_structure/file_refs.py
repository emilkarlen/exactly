import unittest

from exactly_lib.test_case_file_structure import file_refs as sut
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import tmp_user_dir_contents, \
    act_dir_contents
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestRelHome))
    ret_val.addTest(unittest.makeSuite(TestRelCwd))
    ret_val.addTest(unittest.makeSuite(TestRelTmpUser))
    return ret_val


class TestRelHome(unittest.TestCase):
    def test_should_reference_no_value_definitions(self):
        file_reference = sut.rel_home('file.txt')
        self.assertTrue(len(file_reference.value_references_of_paths()) == 0,
                        'File is expected to reference no variable definitions')

    def test_exists_pre_sds(self):
        file_reference = sut.rel_home('file.txt')
        self.assertTrue(file_reference.exists_pre_sds(empty_symbol_table()),
                        'File is expected to exist pre SDS')

    def test_existing_file(self):
        file_reference = sut.rel_home('file.txt')
        with home_and_sds_with_act_as_curr_dir(
                home_dir_contents=DirContents([empty_file('file.txt')])) as home_and_sds:
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assertTrue(file_reference.file_path_pre_sds(environment).exists())
            self.assertTrue(file_reference.file_path_pre_or_post_sds(environment).exists())

    def test_non_existing_file(self):
        file_reference = sut.rel_home('file.txt')
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assertFalse(file_reference.file_path_pre_sds(environment).exists())
            self.assertFalse(file_reference.file_path_pre_or_post_sds(environment).exists())


class TestRelCwd(unittest.TestCase):
    def test_should_reference_no_value_definitions(self):
        file_reference = sut.rel_cwd('file.txt')
        self.assertTrue(len(file_reference.value_references_of_paths()) == 0,
                        'File is expected to reference no variable definitions')

    def test_exists_pre_sds(self):
        file_reference = sut.rel_cwd('file.txt')
        self.assertFalse(file_reference.exists_pre_sds(empty_symbol_table()),
                         'File is expected to not exist pre SDS')

    def test_existing_file(self):
        file_reference = sut.rel_cwd('file.txt')
        with home_and_sds_with_act_as_curr_dir(
                sds_contents=act_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_sds:
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assertTrue(file_reference.file_path_pre_or_post_sds(environment).exists())

    def test_non_existing_file(self):
        file_reference = sut.rel_cwd('file.txt')
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assertFalse(file_reference.file_path_pre_or_post_sds(environment).exists())


class TestRelTmpUser(unittest.TestCase):
    def test_should_reference_no_value_definitions(self):
        file_reference = sut.rel_tmp_user('file.txt')
        self.assertTrue(len(file_reference.value_references_of_paths()) == 0,
                        'File is expected to reference no variable definitions')

    def test_exists_pre_sds(self):
        file_reference = sut.rel_tmp_user('file.txt')
        self.assertFalse(file_reference.exists_pre_sds(empty_symbol_table()),
                         'File is expected to not exist pre SDS')

    def test_existing_file(self):
        file_reference = sut.rel_tmp_user('file.txt')
        with home_and_sds_with_act_as_curr_dir(
                sds_contents=tmp_user_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_sds:
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds, empty_symbol_table())
            self.assertTrue(file_reference.file_path_pre_or_post_sds(environment).exists())

    def test_non_existing_file(self):
        file_reference = sut.rel_tmp_user('file.txt')
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds, empty_symbol_table())
            self.assertFalse(file_reference.file_path_pre_or_post_sds(environment).exists())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
