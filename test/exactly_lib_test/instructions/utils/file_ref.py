import unittest

from exactly_lib.instructions.utils import file_ref as sut
from exactly_lib_test.test_resources.execution.sds_populator import act_dir_contents, tmp_user_dir_contents, \
    tmp_internal_dir_contents
from exactly_lib_test.test_resources.execution.utils import home_and_sds_and_test_as_curr_dir
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file


class TestRelHome(unittest.TestCase):
    def test_exists_pre_eds(self):
        file_reference = sut.rel_home('file.txt')
        self.assertTrue(file_reference.exists_pre_eds,
                        'File is expected to exist pre SDS')

    def test_existing_file(self):
        file_reference = sut.rel_home('file.txt')
        with home_and_sds_and_test_as_curr_dir(
                home_dir_contents=DirContents([empty_file('file.txt')])) as home_and_sds:
            self.assertTrue(file_reference.file_path_pre_eds(home_and_sds.home_dir_path).exists())
            self.assertTrue(file_reference.file_path_pre_or_post_eds(home_and_sds).exists())

    def test_non_existing_file(self):
        file_reference = sut.rel_home('file.txt')
        with home_and_sds_and_test_as_curr_dir() as home_and_sds:
            self.assertFalse(file_reference.file_path_pre_eds(home_and_sds.home_dir_path).exists())
            self.assertFalse(file_reference.file_path_pre_or_post_eds(home_and_sds).exists())


class TestRelCwd(unittest.TestCase):
    def test_exists_pre_eds(self):
        file_reference = sut.rel_cwd('file.txt')
        self.assertFalse(file_reference.exists_pre_eds,
                         'File is expected to not exist pre SDS')

    def test_existing_file(self):
        file_reference = sut.rel_cwd('file.txt')
        with home_and_sds_and_test_as_curr_dir(
                sds_contents=act_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_sds:
            self.assertTrue(file_reference.file_path_pre_or_post_eds(home_and_sds).exists())

    def test_non_existing_file(self):
        file_reference = sut.rel_cwd('file.txt')
        with home_and_sds_and_test_as_curr_dir() as home_and_sds:
            self.assertFalse(file_reference.file_path_pre_or_post_eds(home_and_sds).exists())


class TestRelTmpUser(unittest.TestCase):
    def test_exists_pre_eds(self):
        file_reference = sut.rel_tmp_user('file.txt')
        self.assertFalse(file_reference.exists_pre_eds,
                         'File is expected to not exist pre SDS')

    def test_existing_file(self):
        file_reference = sut.rel_tmp_user('file.txt')
        with home_and_sds_and_test_as_curr_dir(
                sds_contents=tmp_user_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_sds:
            self.assertTrue(file_reference.file_path_pre_or_post_eds(home_and_sds).exists())

    def test_non_existing_file(self):
        file_reference = sut.rel_tmp_user('file.txt')
        with home_and_sds_and_test_as_curr_dir() as home_and_sds:
            self.assertFalse(file_reference.file_path_pre_or_post_eds(home_and_sds).exists())


class TestRelTmpInternal(unittest.TestCase):
    def test_exists_pre_eds(self):
        file_reference = sut.rel_tmp_internal('file.txt')
        self.assertFalse(file_reference.exists_pre_eds,
                         'File is expected to not exist pre SDS')

    def test_existing_file(self):
        file_reference = sut.rel_tmp_internal('file.txt')
        with home_and_sds_and_test_as_curr_dir(
                sds_contents=tmp_internal_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_sds:
            self.assertTrue(file_reference.file_path_pre_or_post_eds(home_and_sds).exists())

    def test_non_existing_file(self):
        file_reference = sut.rel_tmp_internal('file.txt')
        with home_and_sds_and_test_as_curr_dir() as home_and_sds:
            self.assertFalse(file_reference.file_path_pre_or_post_eds(home_and_sds).exists())


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestRelHome))
    ret_val.addTest(unittest.makeSuite(TestRelCwd))
    ret_val.addTest(unittest.makeSuite(TestRelTmpUser))
    ret_val.addTest(unittest.makeSuite(TestRelTmpInternal))
    return ret_val


if __name__ == '__main__':
    unittest.main()
