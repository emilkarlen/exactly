import unittest

from shellcheck_lib.instructions.utils import file_ref as sut
from shellcheck_lib_test.instructions.test_resources.eds_populator import act_dir_contents, tmp_user_dir_contents, \
    tmp_internal_dir_contents
from shellcheck_lib_test.instructions.test_resources.utils import home_and_eds_and_test_as_curr_dir
from shellcheck_lib_test.util.file_structure import DirContents, empty_file


class TestRelHome(unittest.TestCase):
    def test_exists_pre_eds(self):
        file_reference = sut.rel_home('file.txt')
        self.assertTrue(file_reference.exists_pre_eds,
                        'File is expected to exist pre EDS')

    def test_existing_file(self):
        file_reference = sut.rel_home('file.txt')
        with home_and_eds_and_test_as_curr_dir(
                home_dir_contents=DirContents([empty_file('file.txt')])) as home_and_eds:
            self.assertTrue(file_reference.file_path_pre_eds(home_and_eds.home_dir_path).exists())
            self.assertTrue(file_reference.file_path(home_and_eds).exists())

    def test_non_existing_file(self):
        file_reference = sut.rel_home('file.txt')
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            self.assertFalse(file_reference.file_path_pre_eds(home_and_eds.home_dir_path).exists())
            self.assertFalse(file_reference.file_path(home_and_eds).exists())


class TestRelCwd(unittest.TestCase):
    def test_exists_pre_eds(self):
        file_reference = sut.rel_cwd('file.txt')
        self.assertFalse(file_reference.exists_pre_eds,
                         'File is expected to not exist pre EDS')

    def test_existing_file(self):
        file_reference = sut.rel_cwd('file.txt')
        with home_and_eds_and_test_as_curr_dir(
                eds_contents=act_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_eds:
            self.assertTrue(file_reference.file_path(home_and_eds).exists())

    def test_non_existing_file(self):
        file_reference = sut.rel_cwd('file.txt')
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            self.assertFalse(file_reference.file_path(home_and_eds).exists())


class TestRelTmpUser(unittest.TestCase):
    def test_exists_pre_eds(self):
        file_reference = sut.rel_tmp_user('file.txt')
        self.assertFalse(file_reference.exists_pre_eds,
                         'File is expected to not exist pre EDS')

    def test_existing_file(self):
        file_reference = sut.rel_tmp_user('file.txt')
        with home_and_eds_and_test_as_curr_dir(
                eds_contents=tmp_user_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_eds:
            self.assertTrue(file_reference.file_path(home_and_eds).exists())

    def test_non_existing_file(self):
        file_reference = sut.rel_tmp_user('file.txt')
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            self.assertFalse(file_reference.file_path(home_and_eds).exists())


class TestRelTmpInternal(unittest.TestCase):
    def test_exists_pre_eds(self):
        file_reference = sut.rel_tmp_internal('file.txt')
        self.assertFalse(file_reference.exists_pre_eds,
                         'File is expected to not exist pre EDS')

    def test_existing_file(self):
        file_reference = sut.rel_tmp_internal('file.txt')
        with home_and_eds_and_test_as_curr_dir(
                eds_contents=tmp_internal_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_eds:
            self.assertTrue(file_reference.file_path(home_and_eds).exists())

    def test_non_existing_file(self):
        file_reference = sut.rel_tmp_internal('file.txt')
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            self.assertFalse(file_reference.file_path(home_and_eds).exists())


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestRelHome))
    ret_val.addTest(unittest.makeSuite(TestRelCwd))
    ret_val.addTest(unittest.makeSuite(TestRelTmpUser))
    ret_val.addTest(unittest.makeSuite(TestRelTmpInternal))
    return ret_val


if __name__ == '__main__':
    unittest.main()
